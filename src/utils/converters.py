import json

from discord.ext import commands

from models import VerificationMethod


# Prevents the file to be read multiple times
DISCORD_EMOJIS = None
with open("../assets/discord_emojis.json") as f:
    DISCORD_EMOJIS = json.load(f)


class VerificationMethodConverter(commands.Converter):
    """Converts to `VerificationMethod` enum"""

    async def convert(self, ctx: commands.Context, argument):
        try:
            return VerificationMethod(argument.upper())
        except ValueError:
            raise commands.BadArgument(
                message="Failed to convert to verification method"
            )


class UnicodeEmojiConverter(commands.Converter):
    """Custom converter for converting to unicode and Emoji objects

    Returns a tuple of form (EMOJI, is_unicode)
    """

    async def convert(self, ctx, argument):
        if argument.startswith(":"):
            argument = argument[1:]

        if argument.endswith(":"):
            argument = argument[:-1]

        try:
            custom_emoji = await commands.EmojiConverter().convert(ctx, argument)
            return (custom_emoji, False)
        except:
            if argument in DISCORD_EMOJIS.keys():
                return (DISCORD_EMOJIS[argument], True)

            if argument in DISCORD_EMOJIS.values():
                return (argument, True)

            raise commands.EmojiNotFound(argument)
