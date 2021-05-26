import time
import sys, platform

import discord
from discord.ext import commands

from models import Guild, Config, ConfigType, VerificationMethod


class Info(commands.Cog):
    """Basic informational commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Check the bot's latency"""
        pings = []
        number = 0
        typings = time.monotonic()
        await ctx.trigger_typing()
        typinge = time.monotonic()
        typingms = round((typinge - typings) * 1000)
        pings.append(typingms)
        latencyms = round(self.bot.latency * 1000)
        pings.append(latencyms)
        discords = time.monotonic()
        url = "https://discordapp.com/"
        async with self.bot.aio_session.get(url) as resp:
            if resp.status == 200:
                discorde = time.monotonic()
                discordms = round((discorde - discords) * 1000)
                pings.append(discordms)
                discordms = f"{discordms}ms"
            else:
                discordms = "Failed"
        for ms in pings:
            number += ms
        average = round(number / len(pings))
        await ctx.send(
            f"__**Ping Times:**__\nTyping: `{typingms}ms`  |  Latency: `{latencyms}ms`\nDiscord: `{discordms}`  |  Average: `{average}ms`"
        )

    @commands.command()
    async def support(self, ctx: commands.Context):
        """Returns the support server invite-link"""

        await ctx.send(
            "https://discord.gg/y3A9DFyjhV"
        )

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Returns the invite link for bot

        Permissions snowflake is `268725312`

        Permissions
        -----------
        - Manage Roles
        - View Channels
        - Send Messages
        - Manage Messages
        - Embed Links
        - External Emojis
        - Reactions
        """
        permissions_integer = 268725312
        client_id = self.bot.user.id

        await ctx.send(
            f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions_integer}&scope=bot"
        )

    @commands.command()
    async def info(self, ctx: commands.Context):
        """Shows Info about bot"""

        embed = self.bot.embed_gen.get_normal_embed(
            title="Bot Info",
            description=f"""Soteria is a next-gen verification bot utilising the power of captchas
            
            **Bot**
            ------
            - Guilds: {len(self.bot.guilds)}
            - Users: {len(self.bot.users)}

            **Host Environment**
            ----------------------
            - OS/Kernel: {sys.platform}
            - Platform: {platform.platform()}
            - Arch: {platform.architecture()[0]}

            **Developed By**
            ----------------
            - SyedAhkam#5085 (Bot Developer)
            - Распутин#0962 (General Idea and captcha API)

            **Interesting Fact**
            ---------------------
            This bot started as a challenge between two friends-- Syed and Распутин to be exact.
            The challenge was: "One of us would code in Python and other in JS, And later we would judge each other's end-result" (no hate on languages)
            
            Unfortunately, Распутин's busy life did not allow him to pursue the afforementioned challenge-- Hence, The bot in production currently is the one coded by Syed.
            """,
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def status(self, ctx: commands.Context):
        """Check Bot status in your server"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        bot_prefix = guild_obj.get_bot_prefix()
        verification_method = guild_obj.get_verification_method()

        verification_channel = ctx.guild.get_channel(
            await Config.get_value_int(guild_obj, ConfigType.VERIFICATION_CHANNEL)
        )
        verified_role = ctx.guild.get_role(
            await Config.get_value_int(guild_obj, ConfigType.VERIFIED_ROLE)
        )

        is_verification_message_start_set = await Config.exists(
            guild=guild_obj, type_=ConfigType.VERIFICATION_MESSAGE_START
        )
        is_verification_message_success_set = await Config.exists(
            guild=guild_obj, type_=ConfigType.VERIFICATION_MESSAGE_SUCCESS
        )

        reaction_channel = ctx.guild.get_channel(
            await Config.get_value_int(guild_obj, ConfigType.REACTION_CHANNEL)
        )
        reaction_message = await Config.get_value_int(
            guild_obj, ConfigType.REACTION_MESSAGE
        )
        reaction_emoji = await Config.get_value_str(
            guild_obj, ConfigType.REACTION_EMOJI
        )

        embed = self.bot.embed_gen.get_normal_embed(
            title="Bot Status",
            description="""Bot configuration in your server is as follows
            
            **Required**
            ------------
            - Verified Role is always required, regardless of verification method
            - Verification Channel is required, when method is set to channel
            - Reaction Channel is required, when method is set to reaction
            - Reaction Message is required, when method is set to reaction
            - Reaction Emoji is required, when method is set to reaction

            **Defaults**
            -----------
            - Prefix defaults to 's!'
            - Verification Method defaults to 'DM'
            - Verification Start Message
            - Verification Success Message
            """,
        )

        embed.add_field(
            name="Prefix",
            value=f"{f'{bot_prefix} (default prefix)' if bot_prefix == self.bot.DEFAULT_PREFIX else bot_prefix}",
            inline=False,
        )

        embed.add_field(
            name="Verification Method",
            value=f"{f'{verification_method} (default method)' if verification_method == VerificationMethod.DM else verification_method}",
            inline=True,
        )

        embed.add_field(
            name="Verification Channel",
            value=verification_channel.mention
            if verification_channel and hasattr(verification_channel, "mention")
            else f"Not Set (or invalid)",
            inline=True,
        )

        embed.add_field(
            name="Verified Role",
            value=verified_role.mention
            if verified_role and hasattr(verified_role, "mention")
            else f"Not Set!! (This is mandatory to set)",
            inline=True,
        )

        embed.add_field(
            name="Reaction Channel",
            value=reaction_channel.mention
            if reaction_channel and hasattr(reaction_channel, "mention")
            else f"Not Set (or invalid)",
            inline=True,
        )

        embed.add_field(
            name="Reaction Message", value=reaction_message or "Not set", inline=True
        )

        embed.add_field(
            name="Reaction Emoji", value=reaction_emoji or "Not Set", inline=True
        )

        embed.add_field(
            name="Are verification messages set?",
            value=f"Start Message: {'yes' if is_verification_message_start_set else 'no'}\nSuccess Message: {'yes' if is_verification_message_success_set else 'no'}",
            inline=False,
        )

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
