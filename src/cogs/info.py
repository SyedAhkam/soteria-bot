import discord

import time

from discord.ext import commands

class Info(commands.Cog):
    """Basic informational commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
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
    async def test(self, ctx):
        async with self.bot.aio_session.get(self.bot.CAPTCHA_API_URL + 'captcha') as r:
            captcha_base64 = (await r.json())["captcha"][22:]
            captcha_bytes = base64.b64decode(captcha_base64)

            await ctx.send(file=discord.File(BytesIO(captcha_bytes), filename="captcha.png"))

def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
