import discord

from discord.ext import commands

from models import Guild, Config, ConfigType
from utils.converters import VerificationMethodConverter, UnicodeEmojiConverter

# FIXME: permissions


class Setup(commands.Cog):
    """Configure the bot here"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group()
    async def set(self, ctx: commands.Context):
        """Group of commands to customize the bot's behaviour"""

        pass

    @set.command()
    async def prefix(self, ctx: commands.Context, *, new_prefix):
        """Sets the bot prefix"""

        await (await Guild.get(id=ctx.guild.id)).set_bot_prefix(new_prefix)

        await ctx.send(f"Prefix set to `{new_prefix}`")

    @set.command()
    async def verification_method(
        self, ctx: commands.Context, new_method: VerificationMethodConverter
    ):
        """Sets the verification method"""

        await (await Guild.get(id=ctx.guild.id)).set_verification_method(new_method)

        await ctx.send(f"Verification Method set to `{new_method}`")

    @set.command()
    async def verification_channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        """Sets the verification channel"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(
            guild_obj, ConfigType.VERIFICATION_CHANNEL, channel.id
        )
        await ctx.send(f"Set `{channel}` as verification channel.")

    @set.command()
    async def verified_role(self, ctx: commands.Context, role: discord.Role):
        """Sets the verified role"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(guild_obj, ConfigType.VERIFIED_ROLE, role.id)
        await ctx.send(f"Set `{role}` as verified role.")

    @set.command()
    async def verification_start_message(self, ctx: commands.Context, *, message: str):
        """Sets the verification start message"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_str(
            guild_obj, ConfigType.VERIFICATION_MESSAGE_START, message
        )
        await ctx.send(f"Set the verification start message as: ```\n{message}\n```")

    @set.command()
    async def verification_success_message(
        self, ctx: commands.Context, *, message: str
    ):
        """Sets the verification success message"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_str(
            guild_obj, ConfigType.VERIFICATION_MESSAGE_SUCCESS, message
        )
        await ctx.send(f"Set the verification success message as: ```\n{message}\n```")

    @set.command()
    async def reaction_channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        """Sets the reaction channel"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(guild_obj, ConfigType.REACTION_CHANNEL, channel.id)
        await ctx.send(f"Set `{channel}` as reaction channel.")

    @set.command()
    async def reaction_message(
        self, ctx: commands.Context, message: discord.Message
    ):  # FIXME: converting to `discord.Message` could have some caching issues
        """Sets the reaction message"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(guild_obj, ConfigType.REACTION_MESSAGE, message.id)
        await ctx.send(f"Set the reaction message to: ```\n{message.content}\n```")

        # try to react
        is_emoji_unicode = await Config.get_value_bool(
            guild_obj, ConfigType.REACTION_EMOJI
        )

        if is_emoji_unicode:
            emoji = await Config.get_value_str(guild_obj, ConfigType.REACTION_EMOJI)
        else:
            emoji = await ctx.guild.fetch_emoji(
                await Config.get_value_int(guild_obj, ConfigType.REACTION_EMOJI)
            )

        await message.add_reaction(emoji)

    @set.command()
    async def reaction_emoji(self, ctx: commands.Context, emoji: UnicodeEmojiConverter):
        """Sets the reaction emoji"""

        emoji, is_unicode = emoji

        guild_obj = await Guild.get(id=ctx.guild.id)

        # stores is_unicode value
        await Config.set_value_bool(guild_obj, ConfigType.REACTION_EMOJI, is_unicode)

        if is_unicode:
            await Config.set_value_str(guild_obj, ConfigType.REACTION_EMOJI, emoji)
        else:
            await Config.set_value_int(guild_obj, ConfigType.REACTION_EMOJI, emoji.id)

        await ctx.send(f"Set the reaction emoji as: ```\n{emoji}\n```")


def setup(bot: commands.Bot):
    bot.add_cog(Setup(bot))
