from datetime import datetime

import discord


class EmbedGen:
    COLORS = {"normal": 0xF85A5A, "warn": 0xF8D210, "error": 0x541F1F}

    def __init__(self):
        pass

    def get_normal_embed(self, *args, **kwargs):
        return discord.Embed(
            *args, color=self.COLORS["normal"], timestamp=datetime.utcnow(), **kwargs
        )

    def get_warn_embed(self, *args, **kwargs):
        return discord.Embed(
            *args, color=self.COLORS["warn"], timestamp=datetime.utcnow(), **kwargs
        )

    def get_error_embed(self, *args, **kwargs):
        return discord.Embed(
            *args, color=self.COLORS["error"], timestamp=datetime.utcnow(), **kwargs
        )
