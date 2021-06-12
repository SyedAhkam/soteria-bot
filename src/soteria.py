import os
import sys

from pathlib import Path

import aiohttp
import discord
import coloredlogs

from discord.ext import commands
from dotenv import load_dotenv
from tortoise import Tortoise

from models import Guild
from utils.embeds import EmbedGen
from utils.logging import get_bot_logger, setup_discord_logging

# Logs from discord library itself
setup_discord_logging()

# Define Intents
intents = discord.Intents.default()
intents.members = True

# Load environment variables from `.env` file
load_dotenv()


class Soteria(commands.Bot):
    """Subclass of `commands.Bot` for more control"""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=intents,
            owner_id=342545053169877006,
            **kwargs,
        )

        # Logs for obvious reasons
        self.logger = get_bot_logger()

        # Color the logs
        coloredlogs.install(logger=self.logger)

        self.logger.info("Starting up Soteria...")

        # Check if discord token is set, if not exit process
        if not "SOTERIA_DISCORD_TOKEN" in os.environ:
            self.logger.critical("SOTERIA_DISCORD_TOKEN not set!")
            sys.exit(1)

        # Internal bot-level constants
        self._DISCORD_TOKEN = os.getenv("SOTERIA_DISCORD_TOKEN")
        self._DB_URI = os.getenv("SOTERIA_DB_URI")

        # Global bot-level constants
        self.DEFAULT_PREFIX = os.getenv("SOTERIA_DEFAULT_PREFIX", "s!")
        self.PRESENCE_TEXT = os.getenv("SOTERIA_PRESENCE_TEXT", "humans")
        self.CAPTCHA_API_URL = os.getenv("SOTERIA_CAPTCHA_API_URL")
        self.IGNORED_COGS = ()

        # Embed generator
        self.embed_gen = EmbedGen()

        # Load Jishaku
        self.load_extension("jishaku")

        # Start the startup task
        self.startup_task = self.loop.create_task(self.startup())

    @staticmethod
    def is_env_dev():
        """Returns a boolean signifying if bot is running in dev mode"""
        env_value = os.getenv("SOTERIA_ENV_DEV", default="0")
        if env_value == "1":
            return True

        return False

    def _load_cogs(self, directory: os.PathLike):
        """Loads cogs from specified directory

        Parameters
        ----------
        directory: str
            The directory path to load cogs from
        """

        for file in os.listdir(directory):
            filename, ext = os.path.splitext(file)

            if not ext == ".py":
                continue

            if filename in self.IGNORED_COGS:
                continue

            try:
                self.load_extension(
                    f"{directory.name}.{filename}"
                )  # finally, load the cog
            except commands.ExtensionError as e:
                self.logger.critical(f"Failed to load extension: {filename}")
                raise e

            self.logger.info(f"Loaded extension cog: {filename}")

        self.logger.info(f"Loaded {len(self.cogs)} cogs")

    async def _init_db(self, db_uri: str):
        """Initializes database ORM"""

        await Tortoise.init(db_url=db_uri, modules={"models": ["models"]})

        self.logger.info("Generating schemas...")
        await Tortoise.generate_schemas(safe=True)

        self.logger.info("Initialized DB")

    async def _set_presence(self, presence_text: str):
        """Sets the bot presence on startup"""

        activity = discord.Activity(
            type=discord.ActivityType.listening, name=presence_text
        )

        await self.change_presence(status=discord.Status.online, activity=activity)
        self.logger.info(f"Set bot presence to '{presence_text}'")

    async def get_prefix(self, message: discord.Message):
        """Callable for `command_prefix`

        Parameters
        ----------
        message: discord.Message
            The message to get prefix for
        """

        # If it's not a guild, just return default prefix
        if not message.guild:
            return commands.when_mentioned_or(self.DEFAULT_PREFIX)(self, message)

        # Else fetch the custom prefix for that guild
        custom_prefix = (
            await Guild.get_or_create(
                {
                    "name": message.guild.name,
                    "owner_id": message.guild.owner_id,
                    "bot_prefix": self.DEFAULT_PREFIX,
                },
                id=message.guild.id,
            )
        )[0].get_bot_prefix()

        return commands.when_mentioned_or(custom_prefix)(self, message)

    async def on_guild_join(self, guild: discord.Guild):
        """Event emitted on guild joins"""
        self.logger.info(f"I got added to a new server: {guild}")

        # Creates a new `Guild` object
        await Guild.create(
            id=guild.id,
            name=guild.name,
            owner_id=guild.owner_id,
            bot_prefix=self.DEFAULT_PREFIX,
        )

    async def on_guild_remove(self, guild: discord.Guild):
        """Event emitted on guild removes"""
        self.logger.info(f"I got removed from this server: {guild}")

        # Deletes the `Guild` object
        await (await Guild.get(id=guild.id)).delete()

    async def on_message(self, message: discord.Message):
        """Event emmited on every message create

        This is responsible for the following:
            - Reply back with prefix, when mentioned
        """

        if message.author == self.user:  # ignore, if the message by the bot itself
            return

        if message.author.bot:  # ignore if message author is a bot
            return

        if len(message.mentions) > 1:  # ignore, if more than 1 mentions
            await self.process_commands(message)
            return

        if len(message.content.split()) > 1:  # ignore, if more than 1 words
            await self.process_commands(message)
            return

        if self.user.id in message.raw_mentions:  # if bot user was mentioned
            prefixes = (await self.get_prefix(message))[1:]

            await message.channel.send(f"My prefixes are: {', '.join(prefixes)}")

        await self.process_commands(
            message
        )  # make sure other commands are processed after this event

    async def startup(self):
        """A custom `asyncio.Task` which runs on bot's initial bootup (startup)

        This is responsible for the following:
            - Load cogs
            - Initializes database connections
            - Set a discord presence
        """

        await self.wait_until_ready()  # waits until the bot's internal cache is ready

        self.logger.info(f"Connected to discord as {self.user}")

        # Load cogs
        self._load_cogs(Path(os.path.join(Path(__file__).parent, "cogs")))

        # Init DB
        await self._init_db(self._DB_URI)

        # Set Presence
        await self._set_presence(self.PRESENCE_TEXT)

        # This can only be set inside an async function
        self.aio_session = aiohttp.ClientSession()

        self.logger.info("Bot is ready for use!")

    async def close(self):
        """Closes the underlying connections for a clean exit"""

        self.logger.warning("Closing connections...")

        await Tortoise.close_connections()

        if not self.startup_task.cancelled():
            self.startup_task.cancel()

        if not self.aio_session.closed:
            await self.aio_session.close()

        self.logger.critical("Bye!")

        await super().close()


if __name__ == "__main__":
    bot = Soteria()

    bot.run(bot._DISCORD_TOKEN)
