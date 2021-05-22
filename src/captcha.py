import base64
import json

from io import BytesIO

import discord


class Captcha:
    """Encapsulates all the captcha logic"""

    # Constants
    captcha_gen_endpoint = "captcha"
    captcha_verify_endpoint = "verify"

    def __init__(self):
        # Bind attributes
        self.aio_session = None
        self.captcha_api_base_url = None
        self.captcha_json = None
        self.captcha_base64 = None
        self.captcha_uuid = None
        self.captcha_bytes = None

    @classmethod
    async def new(cls, captcha_api_base_url: str, aio_session):
        """Fetches and creates a new instance"""

        async with aio_session.get(
            captcha_api_base_url + cls.captcha_gen_endpoint
        ) as resp:
            new_captcha = cls()

            new_captcha.captcha_api_base_url = captcha_api_base_url
            new_captcha.aio_session = aio_session

            new_captcha.captcha_json = await resp.json()

            new_captcha.captcha_uuid = new_captcha.captcha_json["uuid"]
            new_captcha.captcha_base64 = new_captcha.captcha_json["captcha"][22:]

            return new_captcha

    async def verify(self, user_response: str) -> bool:
        """Verifies the instance with user response"""

        async with self.aio_session.get(
            self.captcha_api_base_url + self.captcha_verify_endpoint,
            json={"uuid": self.captcha_uuid, "captcha": user_response},
        ) as resp:
            if not resp.status == 200:
                return False

            return True

    def decode(self) -> bytes:
        """Decodes the captcha into bytes"""

        self.captcha_bytes = base64.b64decode(self.captcha_base64)
        return self.captcha_bytes

    def get_discord_file(self, file_name: str) -> discord.File:
        """Returns a `discord.File` object"""
        return discord.File(BytesIO(self.captcha_bytes), filename=file_name)
