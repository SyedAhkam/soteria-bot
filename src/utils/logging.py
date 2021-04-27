import logging


def get_bot_logger():
    bot_logger = logging.getLogger("bot")
    bot_logger.setLevel(logging.INFO)
    bot_logger_handler = logging.StreamHandler()
    bot_logger_handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    bot_logger.addHandler(bot_logger_handler)

    return bot_logger


def setup_discord_logging():
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.DEBUG)
    discord_logger_handler = logging.FileHandler(
        filename="../../discord.log", encoding="utf-8", mode="w"
    )
    discord_logger_handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    discord_logger.addHandler(discord_logger_handler)

    return discord_logger
