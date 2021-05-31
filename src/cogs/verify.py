import asyncio
import typing

import discord
from discord.ext import commands

from captcha import Captcha
from models import Config, ConfigType, Guild, VerificationMethod
from utils.extras import format_placeholders


class Verify(commands.Cog):
    """Main verification"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_gen = bot.embed_gen

    async def is_verified_role_set(self, guild: discord.Guild):
        guild_obj = await Guild.get(id=guild.id)

        return await Config.exists(guild=guild_obj, type_=ConfigType.VERIFIED_ROLE)

    async def get_text_input(
        self,
        channel: discord.TextChannel,
        member_or_user: typing.Union[discord.Member, discord.User],
        timeout=None,
    ) -> discord.Message:
        """Waits for the user for input and returns it"""

        def text_wait_for_check(new_msg: discord.Message):
            return new_msg.author == member_or_user and new_msg.channel == channel

        return await self.bot.wait_for(
            "message", check=text_wait_for_check, timeout=timeout
        )

    async def verify_text_input(self, captcha: Captcha, input_msg: discord.Message):
        """Verifies user's captcha solve attempt"""

        return await captcha.verify(input_msg.content)

    async def add_verified_role(self, member: discord.Member):
        """Adds the verified role to member verified"""

        guild = member.guild

        guild_obj = await Guild.get(id=guild.id)
        verified_role_id = await Config.get_value_int(
            guild_obj, ConfigType.VERIFIED_ROLE
        )

        if not verified_role_id:  # ignore if not set
            return

        verified_role = guild.get_role(verified_role_id)
        await member.add_roles(verified_role, reason="Verified User")

        return verified_role

    async def display_captcha(
        self,
        captcha_file: discord.File,
        channel: typing.Union[discord.TextChannel, discord.DMChannel],
        guild: discord.Guild,
        member: discord.member,
        mention=None,
    ):
        """Displays the captcha in an embed"""

        guild_obj = await Guild.get(id=guild.id)

        # fetch the verification message for start, if not set; use default
        verification_message = await Config.get_value_str(
            guild_obj, ConfigType.VERIFICATION_MESSAGE_START
        )
        if not verification_message:
            verification_message = "The server you just joined requires manual verification.\n\n**Just reply me with the characters displayed below. (case-sensitive)**"

        formatted_verification_message = format_placeholders(
            verification_message,
            {
                "guild_name": guild.name,
                "guild_id": guild.id,
                "guild_total_members": len(guild.members),
                "guild_humans": len(
                    [member for member in guild.members if not member.bot]
                ),
                "member_name": member.name,
                "member_id": member.id,
                "member_mention": member.mention,
                "member_tag": str(member),
                "member_discrim": member.discriminator,
            },
        )

        embed = self.embed_gen.get_normal_embed(
            title="Verification Required", description=formatted_verification_message
        )
        embed.set_image(url="attachment://captcha.png")
        embed.set_footer(
            text=f"This prompt will timeout in 60 secs | {guild}",
            icon_url=self.bot.user.avatar_url,
        )

        await channel.send(f"{mention or ''}", embed=embed, file=captcha_file)

    async def on_timeout(
        self,
        channel: typing.Union[discord.TextChannel, discord.DMChannel],
        guild: discord.Guild,
        mention=None,
    ):
        """Executes after verification message was timed-out"""

        embed = self.embed_gen.get_error_embed(
            title="Verification Timed Out",
            description="Oops! Seems like you didn't respond in time.\n\nBut, It's fine! You can start the verification process again using the command `verify`",
        )
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="Notice me pls :c")

        await channel.send(f"{mention or ''}", embed=embed)

    async def on_fail(
        self,
        member_or_user: typing.Union[discord.Member, discord.User],
        channel: typing.Union[discord.TextChannel, discord.DMChannel],
        guild: discord.Guild,
        mention=None,
    ):
        """Executes after verification was failed"""

        embed = self.embed_gen.get_warn_embed(
            title="Verification Failed ",
            description="Oh no! That's not the correct answer!\n\n**Would you like to try again?**",
        )
        embed.set_footer(
            text="Reply back with Y or N", icon_url=self.bot.user.avatar_url
        )

        await channel.send(f"{mention or ''}", embed=embed)

        try:
            reply_msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == member_or_user and m.channel == channel,
                timeout=60,
            )
        except:
            await self.on_timeout(channel, guild, mention=mention)
            return

        # Dangerous recursion here
        if reply_msg.content.upper() == "Y":
            await self.handle_text_verification_methods(member_or_user, guild)

        elif reply_msg.content.upper() == "N":
            await channel.send(
                "Bye! You can start the verification process again using the command `verify`"
            )
        else:
            await self.on_fail(member_or_user, channel, guild, mention=mention)

    async def on_success(
        self,
        member_or_user: typing.Union[discord.Member, discord.User],
        channel: typing.Union[discord.TextChannel, discord.DMChannel],
        guild: discord.Guild,
        mention=None,
    ):
        """Executes after verification was successful"""

        member = guild.get_member(
            member_or_user.id
        )  # make sure we have a member object

        role = await self.add_verified_role(member)

        guild_obj = await Guild.get(id=guild.id)

        # fetch the verification message for success, if not set; use default
        verification_message = await Config.get_value_str(
            guild_obj, ConfigType.VERIFICATION_MESSAGE_SUCCESS
        )
        if not verification_message:
            verification_message = "Good Job! You have been verified!\n\n**I have given you the role `{verified_role_name}`**"

        formatted_verification_message = format_placeholders(
            verification_message,
            {
                "guild_name": guild.name,
                "guild_id": guild.id,
                "guild_total_members": len(guild.members),
                "guild_humans": len(
                    [member for member in guild.members if not member.bot]
                ),
                "member_name": member.name,
                "member_id": member.id,
                "member_mention": member.mention,
                "member_tag": str(member),
                "member_discrim": member.discriminator,
                "verified_role_name": role.name,
                "verified_role_id": role.id,
                "verified_role_mention": role.mention,
            },
        )

        embed = self.embed_gen.get_normal_embed(
            title="Verification Successful", description=formatted_verification_message
        )

        await channel.send(f"{mention or ''}", embed=embed)

    async def start_dm_verification(
        self,
        member_or_user: typing.Union[discord.Member, discord.User],
        guild: discord.Guild,
    ):
        """Starts verification using DM method"""

        captcha = await Captcha.new(self.bot.CAPTCHA_API_URL, self.bot.aio_session)

        captcha.decode()
        captcha_file = captcha.get_discord_file("captcha.png")

        await self.display_captcha(
            captcha_file,
            (await member_or_user.create_dm()),
            guild,
            (guild.get_member(member_or_user.id)),  # to make sure, its a member object
        )

        try:
            user_input = await self.get_text_input(
                member_or_user.dm_channel, member_or_user, timeout=60
            )
        except asyncio.TimeoutError:
            await self.on_timeout(member_or_user, guild)
            return

        result = await self.verify_text_input(captcha, user_input)

        if result is False:
            return await self.on_fail(member_or_user, member_or_user.dm_channel, guild)

        await self.on_success(member_or_user, member_or_user.dm_channel, guild)

    async def start_channel_verification(
        self,
        member: discord.Member,
        verification_channel: discord.TextChannel,
        guild: discord.Guild,
    ):
        """Starts verification using channel method"""

        captcha = await Captcha.new(self.bot.CAPTCHA_API_URL, self.bot.aio_session)

        captcha.decode()
        captcha_file = captcha.get_discord_file("captcha.png")

        await self.display_captcha(
            captcha_file, verification_channel, guild, member, mention=member.mention
        )

        try:
            user_input = await self.get_text_input(
                verification_channel, member, timeout=60
            )
        except asyncio.TimeoutError:
            await self.on_timeout(
                verification_channel,
                verification_channel.guild,
                mention=member.mention,
            )
            return

        result = await self.verify_text_input(captcha, user_input)

        if result is False:
            return await self.on_fail(
                member,
                verification_channel,
                verification_channel.guild,
                mention=member.mention,
            )

        await self.on_success(
            member,
            verification_channel,
            verification_channel.guild,
            mention=member.mention,
        )

    async def handle_text_verification_methods(
        self,
        member_or_user: typing.Union[discord.Member, discord.User],
        guild: discord.Guild,
        invocation_channel: discord.TextChannel = None,
    ):
        """Resolves the verification method setting for the guild and verifies accordingly"""

        verification_method = (await Guild.get(id=guild.id)).get_verification_method()

        # If verified role is not set; ignore
        if not (await self.is_verified_role_set(guild)):
            return

        if verification_method == VerificationMethod.DM:
            if invocation_channel and isinstance(
                invocation_channel, discord.TextChannel
            ):
                await invocation_channel.send(
                    "Starting verification process in DM's..."
                )

            return await self.start_dm_verification(member_or_user, guild)

        if verification_method == VerificationMethod.CHANNEL:

            guild_obj = await Guild.get(id=guild.id)
            verification_channel_id = await Config.get_value_int(
                guild_obj, ConfigType.VERIFICATION_CHANNEL
            )

            verification_channel = guild.get_channel(verification_channel_id)

            return await self.start_channel_verification(
                member_or_user, verification_channel, guild
            )

        # if somehow, method is set to reaction and verify command was used
        if invocation_channel:
            await invocation_channel.send(
                "Verification method is set to reaction.\nPlease react to verification message in order to continue verification process."
            )

    async def start_reaction_verification(
        self,
        member: discord.Member,
        guild: discord.Guild,
        channel_id: int,
        message_id: int,
        reaction_emoji: discord.PartialEmoji,
    ):
        """Starts verification using reaction method"""

        guild_obj = await Guild.get_or_none(id=guild.id)
        if not guild_obj:
            self.bot.logger.warn(f"Ignored guild_obj")
            return

        if (
            not guild_obj.verification_method == VerificationMethod.REACTION
        ):  # if verification method is not REACTION; return
            self.bot.logger.warn(f"Ignored verification_method")
            return

        reaction_channel_id = await Config.get_value_int(
            guild_obj, ConfigType.REACTION_CHANNEL
        )
        if not reaction_channel_id:
            self.bot.logger.warn(f"Ignored reaction channel")
            return

        if (
            not channel_id == reaction_channel_id
        ):  # check if channel is the same as reaction channel in db
            return

        reaction_message = await Config.get_value_int(
            guild_obj, ConfigType.REACTION_MESSAGE
        )
        if (
            not message_id == reaction_message
        ):  # check if message is the same as reaction message in db
            self.bot.logger.warn(f"Ignored reaction message")
            return

        is_unicode = await Config.get_value_bool(guild_obj, ConfigType.REACTION_EMOJI)
        if is_unicode:
            emoji = await Config.get_value_str(guild_obj, ConfigType.REACTION_EMOJI)
        else:
            emoji = self.bot.get_emoji(
                await Config.get_value_int(guild_obj, ConfigType.REACTION_EMOJI)
            )

        if str(reaction_emoji) == str(
            emoji
        ):  # check if emoji is the same as reaction emoji in db
            await self.on_success(member, (await member.create_dm()), guild)

    @commands.Cog.listener(name="on_member_join")
    async def handle_joins(self, member: discord.Member):
        """Starts automatic verification for new members"""

        await self.handle_text_verification_methods(member, member.guild)

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def handle_reactions(self, payload: discord.RawReactionActionEvent):
        """Handles new reactions detected"""
        if not payload:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        if member == guild.me:  # ignore if reaction by bot itself
            return

        await self.start_reaction_verification(
            member, guild, payload.channel_id, payload.message_id, payload.emoji
        )

    @commands.command()
    @commands.max_concurrency(
        1, per=commands.BucketType.user
    )  # to prevent spam by same user
    async def verify(self, ctx: commands.Context, guild: discord.Guild = None):
        """Starts the verification process manually

        This could be used when failed the first automatic attempt by the bot.

        **Arguments**
        --------------
        guild: discord guild (optional)

        **Accepts**
        ------------
        - guild id
        - guild name (maybe)

        **Notes**
        ----------
        - `guild` is a required argument when command is invoked inside DM's
        - covers only text based verification
        """

        if not ctx.guild and not guild:
            await ctx.send(
                "`guild` is a required argument when command is invoked in a DM"
            )
            return

        guild = ctx.guild or guild

        guild_obj = await Guild.get(id=guild.id)
        verified_role_id = await Config.get_value_int(
            guild_obj, ConfigType.VERIFIED_ROLE
        )

        if not verified_role_id:  # ignore if not set
            return await ctx.send(
                "Verified role is not set. Please contact the server admins."
            )

        verified_role = guild.get_role(verified_role_id)
        member = guild.get_member(ctx.author.id)  # ensure it's a member object

        if verified_role in member.roles:
            await ctx.send("You are already verified!")
            return

        await self.handle_text_verification_methods(
            ctx.author, guild, invocation_channel=ctx.channel
        )

    @verify.error
    async def verify_error(self, ctx: commands.Context, error):
        """Local command error handler for verify"""

        if isinstance(error, commands.GuildNotFound):
            await ctx.send(
                "Invalid guild provided.\nThis should be one of these: Guild ID, Guild Name (maybe)"
            )


def setup(bot: commands.Bot):
    bot.add_cog(Verify(bot))
