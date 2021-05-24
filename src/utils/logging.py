import logging
import os

from pathlib import Path

def get_bot_logger(logging_level=logging.INFO):
    bot_logger = logging.getLogger("bot")
    bot_logger.setLevel(logging_level)

    handler = logging.StreamHandler()
    handler.setFormatter("%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s")

    bot_logger.addHandler(handler)

    return bot_logger

def setup_discord_logging(logging_level=logging.DEBUG):
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging_level)

    handler = logging.FileHandler(
        filename=os.path.join(Path(__file__).parent.parent.parent, 'discord.log')
    )

    discord_logger.addHandler(handler)
