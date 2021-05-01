from discord.ext import commands


class AdminPermsRequired(commands.CommandError):
    """Custom exception raised when admin perms are required"""

    def __init__(message=None):
        super().__init__(message=message)


class UserBlacklistedError(commands.CommandError):
    """Custom exception raised when user is blacklisted"""

    def __init__(message=None, global_=False):
        super().__init__(message=message)
        self.global_ = global_
