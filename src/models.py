import typing

from tortoise.models import Model
from tortoise import fields

from enum import Enum

class VerificationMethod(str, Enum):
    """An `Enum` storing verification types

    DM: Perform verification process in direct messages
    CHANNEL: Perform verification process in guild channel
    REACTION: Perform verification process using reactions in guild channel
    """

    DM = "DM"
    CHANNEL = "CHANNEL"
    REACTION = "REACTION"

class ConfigType(str, Enum):
    """An `Enum` storing config types
    
    VERIFICATION_CHANNEL: Stores the verification channel ID
    VERIFIED_ROLE: Stores the verified role ID
    """
    
    VERIFICATION_CHANNEL = "VERIFICATION_CHANNEL"
    VERIFIED_ROLE = "VERIFIED_ROLE"

class Guild(Model):
    """Database Model representing a discord `Guild`
    
    Fields
    ------
    id : int
        Guild's ID
    name : str
        Guild's name
    owner_id : int
        Guild owner's ID
    bot_prefix : str
        Bot prefix setting in the guild
    """
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=120)
    owner_id = fields.BigIntField()
    bot_prefix = fields.CharField(max_length=10)
    verification_method = fields.CharEnumField(VerificationMethod, default=VerificationMethod.DM)

    def __int_(self):
        return self.id

    def __str__(self):
        return self.name

    def get_bot_prefix(self):
        """Returns the bot prefix"""
        return self.bot_prefix

    async def set_bot_prefix(self, new_prefix):
        """Sets the bot prefix and update the instance"""
        self.bot_prefix = new_prefix

        await self.save(update_fields=["bot_prefix"])
    
    def get_verification_method(self):
        """Returns the verification method"""
        return self.verification_method

    async def set_verification_method(self, new_verification_method: VerificationMethod):
        """Sets the verification method and update the instance"""
        self.verification_method = new_verification_method

        await self.save(update_fields=["verification_method"])


class Config(Model):
    """Database Model for storing guild specific config values"""
    guild: Guild = fields.ForeignKeyField("models.Guild", related_name="configs")
    type_ = fields.CharEnumField(ConfigType, source_field="type")
    value_int = fields.BigIntField(null=True)
    value_str = fields.CharField(max_length=2000, null=True)
    value_json = fields.JSONField(null=True)

    def __str__(self):
        return self.value_str

    def __int__(self):
        return self.value_int

    @staticmethod
    async def get_value_str(guild: Guild, type_: ConfigType):
        """Gets the value string for a specific guild with a type"""
        if not (config := await Config.get_or_none(guild=guild, type_=type_)):
            return
        return config.value_str

    @staticmethod
    async def get_value_int(guild: Guild, type_: ConfigType):
        """Gets the value int for a specific guild with a type"""
        if not (config := await Config.get_or_none(guild=guild, type_=type_)):
            return
        return config.value_int
    
    @staticmethod
    async def get_value_json(guild: Guild, type_: ConfigType):
        """Gets the value json for a specific guild with a type"""
        if not (config := await Config.get_or_none(guild=guild, type_=type_)):
            return
        return config.value_json
    
    @staticmethod
    async def set_value_str(guild: Guild, type_: ConfigType, value: str):
        """Sets or creates a config object with the specified value str for a guild"""
        config = await Config.get_or_create(
            {
                "value_str": value
            },
            guild=guild,
            type_=type_
        )
        if not config[1]:
            config[0].value_int=value
            await config[0].save(update_fields=['value_str'])
        
        return config
    
    @staticmethod
    async def set_value_int(guild: Guild, type_: ConfigType, value: int):
        """Sets or creates a config object with the specified value int for a guild"""
        config = await Config.get_or_create(
            {
                "value_int": value
            },
            guild=guild,
            type_=type_
        )
        if not config[1]:
            config[0].value_int=value
            await config[0].save(update_fields=['value_int'])
        
        return config

    @staticmethod
    async def set_value_json(guild: Guild, type_: ConfigType, value: typing.Union[dict, list]):
        """Sets or creates a config object with the specified value json for a guild"""
        config = await Config.get_or_create(
            {
                "value_json": value
            },
            guild=guild,
            type_=type_
        )
        if not config[1]:
            config[0].value_json=value
            await config[0].save(update_fields=['value_json'])
        
        return config
