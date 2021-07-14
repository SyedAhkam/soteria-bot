import discord
from discord.ext import commands

from models import Config, ConfigType, Guild
from utils.converters import UnicodeEmojiConverter, VerificationMethodConverter

# TODO: reset commmand or allow users to pass in None
# TODO: Test commands
# FIXME: cache issue in reaction method


class Setup(commands.Cog):
    """Configure the bot here"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.group()
    async def set(self, ctx: commands.Context):
        """Group of commands to customize the bot's behaviour"""

        if not ctx.invoked_subcommand:
            await ctx.send_help(self.set)

    @set.command()
    async def prefix(self, ctx: commands.Context, *, new_prefix):
        """Sets the bot prefix

        **Arguments**
        --------------
        `new_prefix`: str
            The string you intend to set as bot prefix
        """

        await (await Guild.get(id=ctx.guild.id)).set_bot_prefix(new_prefix)

        await ctx.send(f"Prefix set to `{new_prefix}`")

    @set.command(aliases=["verification-method", "vm"])
    async def verification_method(
        self, ctx: commands.Context, new_method: VerificationMethodConverter
    ):
        """Sets the verification method

        **Arguments**
        --------------
        `new_method`: str
            The new method to use while verifying users

        **Accepts**
        ------------
        - dm
        - channel
        - reaction
        """

        await (await Guild.get(id=ctx.guild.id)).set_verification_method(new_method)

        await ctx.send(f"Verification Method set to `{new_method}`")

    @set.command(aliases=["verification-channel", "vc"])
    async def verification_channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        """Sets the verification channel

        This channel is used while verification method is set to DM.

        **Arguments**
        --------------
        `channel`: discord channel
            The new channel to set as a verification channel

        **Accepts**
        ------------
        - channel id
        - channel mention
        - channel name
        """

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(
            guild_obj, ConfigType.VERIFICATION_CHANNEL, channel.id
        )
        await ctx.send(f"Set `{channel}` as verification channel.")

    @set.command(aliases=["verified-role", "vr"])
    async def verified_role(self, ctx: commands.Context, role: discord.Role):
        """Sets the verified role

        This role is added to users after they successfully complete verification.

        **Arguments**
        --------------
        `role`: discord role
            The role to set as a verified role

        **Accepts**
        ------------
        - role id
        - role mention
        - role name
        """

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(guild_obj, ConfigType.VERIFIED_ROLE, role.id)
        await ctx.send(f"Set `{role}` as verified role.")

    @set.command(aliases=["verification-start-message", "vstm"])
    async def verification_start_message(self, ctx: commands.Context, *, message: str):
        """Sets the verification start message

        This could be customized to show users a customized message on verification start.

        Some placeholders could be used to personalize the message (list below)

        **Arguments**
        --------------
        `message`: str
            A string of text to be used as verification start message

        **Placeholders**
        -----------------
        - `{guild_name}` gives you the guild/server name
        - `{guild_id}` gives you the guild/server id
        - `{guild_total_memberts}` gives you the total member count including bots
        - `{guild_humans}` gives you the member count excluding bots
        - `{member_name}` gives you the member's name
        - `{member_id}` gives you the member's id
        - `{member_mention}` gives you the member's mention
        - `{member_tag}` gives you the member's tag
        - `{member_discrim}` gives you the member's discriminator

        **NOTE**: If an unknown placeholder is detected it would be replaced with an empty string
        """

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_str(
            guild_obj, ConfigType.VERIFICATION_MESSAGE_START, message
        )
        await ctx.send(f"Set the verification start message as: ```\n{message}\n```")

    @set.command(aliases=["verification-success-message", "vscm"])
    async def verification_success_message(
        self, ctx: commands.Context, *, message: str
    ):
        """Sets the verification success message

        This could be customized to show users a customized message upon successful verification attempt.

        Some placeholders could be used to personalize the message (list below)

        **Arguments**
        --------------
        `message`: str
            A string of text to be used as verification success message

        **Placeholders**
        -----------------
        - `{guild_name}` gives you the guild/server name
        - `{guild_id}` gives you the guild/server id
        - `{guild_total_memberts}` gives you the total member count including bots
        - `{guild_humans}` gives you the member count excluding bots
        - `{member_name}` gives you the member's name
        - `{member_id}` gives you the member's id
        - `{member_mention}` gives you the member's mention
        - `{member_tag}` gives you the member's tag
        - `{member_discrim}` gives you the member's discriminator
        - `{verified_role_name}` gives you the verified-role's name
        - `{verified_role_id}` gives you the verfied-role's id
        - `{verified_role_mention}` gives you the verified-role as a mention

        **NOTE**: If an unknown placeholder is detected it would be replaced with an empty string
        """

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_str(
            guild_obj, ConfigType.VERIFICATION_MESSAGE_SUCCESS, message
        )
        await ctx.send(f"Set the verification success message as: ```\n{message}\n```")

    @set.command(aliases=["reaction-channel", "rc"])
    async def reaction_channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        """Sets the reaction channel

        This is used while verification mode is set to "reaction".

        **Arguments**
        --------------
        `channel`: discord channel
            The channel to be set as a reaction channel

        **Accepts**
        ------------
        - channel id
        - channel mention
        - channel name
        """

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(guild_obj, ConfigType.REACTION_CHANNEL, channel.id)
        await ctx.send(f"Set `{channel}` as reaction channel.")

    @set.command(aliases=["reaction-message", "rm"])
    async def reaction_message(
        self, ctx: commands.Context, message: discord.Message
    ):  # FIXME: converting to `discord.Message` could have some caching issues
        """Sets the reaction message

        This enables the bot to check for reactions only on this message.

        **Arguments**
        --------------
        `message`: discord message
            The message to set as reaction message

        **Accepts**
        ------------
        - message id
        """

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(guild_obj, ConfigType.REACTION_MESSAGE, message.id)
        await ctx.send(f"Set the reaction message to: ```\n{message.content}\n```")

        # try to react
        is_emoji_unicode = await Config.get_value_bool(
            guild_obj, ConfigType.REACTION_EMOJI
        )

        try:
            if is_emoji_unicode:
                emoji = await Config.get_value_str(guild_obj, ConfigType.REACTION_EMOJI)
            else:
                emoji = await ctx.guild.fetch_emoji(
                    await Config.get_value_int(guild_obj, ConfigType.REACTION_EMOJI)
                )

            await message.add_reaction(emoji)
        except discord.HTTPException:
            await ctx.send(
                "Failed to add reaction to message. Did you set reaction emoji and it's valid?"
            )

    @set.command(aliases=["reaction-emoji", "re"])
    async def reaction_emoji(self, ctx: commands.Context, emoji: UnicodeEmojiConverter):
        """Sets the reaction emoji

        This enables the bot to respond to reaction events only when the emoji matches.

        **Arguments**
        --------------
        `emoji`: unicode|custom discord emoji
            The emoji to be set as reaction emoji

        **Accepts**
        ------------
        - unicode emoji like 😒
        - custom emoji using it's ID
        - custom emoji mention
        - custom emoji name (could work)
        """

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
