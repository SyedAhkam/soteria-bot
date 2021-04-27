import discord

from discord.ext import commands

from models import Guild, Config, ConfigType
from utils.converters import VerificationMethodConverter

#FIXME: permissions

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
    async def verification_method(self, ctx: commands.Context, new_method: VerificationMethodConverter):
        """Sets the verification method"""

        await (await Guild.get(id=ctx.guild.id)).set_verification_method(new_method)

        await ctx.send(f"Verification Method set to `{new_method}`")

    @set.command()
    async def verification_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the verification channel"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(
            guild_obj,
            ConfigType.VERIFICATION_CHANNEL,
            channel.id
        )
        await ctx.send(f"Set `{channel}` as verification channel.")

    @set.command()
    async def verified_role(self, ctx: commands.Context, role: discord.Role):
        """Sets the verified role"""

        guild_obj = await Guild.get(id=ctx.guild.id)

        await Config.set_value_int(
            guild_obj,
            ConfigType.VERIFIED_ROLE,
            role.id
        )
        await ctx.send(f"Set `{role}` as verified role.")

def setup(bot: commands.Bot):
    bot.add_cog(Setup(bot))
