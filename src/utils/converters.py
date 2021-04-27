from discord.ext import commands

from models import VerificationMethod

class VerificationMethodConverter(commands.Converter):
    """Converts to `VerificationMethod` enum"""

    async def convert(self, ctx: commands.Context, argument):
        try:
            return VerificationMethod(argument.upper())
        except ValueError:
            raise commands.BadArgument(message="Failed to convert to verification method")
