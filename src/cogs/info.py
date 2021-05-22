import time

import discord
from discord.ext import commands


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
    
def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
