from discord.ext import commands

from utils import exceptions


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_gen = bot.embed_gen
        self.ignored = commands.CommandNotFound

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Using on_command_error as an error handler."""
        
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return
        
        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        
        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)
        
        # These exceptions would be ignored
        if isinstance(error, self.ignored):
            return

        if isinstance(error, exceptions.AdminPermsRequired):
            embed = self.embed_gen.get_error_embed(
                title="Admin Perms Required",
                description="Sorry, This command requires admin perms to execute.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, exceptions.UserBlacklistedError):
            if error.global_:
                embed = self.embed_gen.get_error_embed(
                    title="Blacklisted",
                    description="Sorry, You've been blacklisted from using any of my commands globally.\nPlease stop trying to use them.",
                )
                await ctx.send(embed=embed)
            else:
                embed = self.embed_gen.get_error_embed(
                    title="Blacklisted",
                    description="Sorry, You've been blacklisted from using any of my commands in this server.\nPlease stop trying to use them.",
                )
                await ctx.send(embed=embed)

            return

        if isinstance(error, commands.DisabledCommand):
            embed = self.embed_gen.get_error_embed(
                title="Disabled Command",
                description="Sorry, This command has been disabled by the owner of bot.\nPlease stop trying to use it.",
            )
            await ctx.send(embed=embed)
            return

        # Im a little confused about this error
        if isinstance(error, commands.ConversionError):
            embed = self.embed_gen.get_error_embed(
                title="Conversion Error",
                description="Sorry, I failed to convert your input.\nMaybe the command expects a number and you provided a text instead?",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CheckFailure):
            embed = self.embed_gen.get_error_embed(
                title="Check Failure",
                description="Sorry, It doesn't seem like you're allowed to access this command."
            )
            await ctx.send(embed=embed)

        if isinstance(error, commands.NoPrivateMessage):
                embed = self.embed_gen.get_error_embed(
                    title="No Private Message",
                    description="Sorry, This command can't be used in private messages.",
                )
                await ctx.send(embed=embed)
                return

        if isinstance(error, commands.PrivateMessageOnly):
            embed = self.embed_gen.get_error_embed(
                title="Private Message Only",
                description="Sorry, This command can only be used in private messages.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.NotOwner):
            embed = self.embed_gen.get_error_embed(
                title="Not Owner",
                description="Sorry, This command can only be used by the owner of bot.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MissingPermissions):
            required_perms = ""
            for perm in error.missing_perms:
                required_perms += f"- {perm}"
                required_perms += "\n"

            embed = self.embed_gen.get_error_embed(
                title="Missing Permmisions",
                description=f"Sorry, You need to have these permissions to run this command:\n``{required_perms}``",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BotMissingPermissions):
            required_perms = ""
            for perm in error.missing_perms:
                required_perms += f"- {perm}"
                required_perms += "\n"

            embed = self.embed_gen.get_error_embed(
                title="Bot Missing Permmisions",
                description=f"Sorry, I need to have these permissions to run this command:\n``{required_perms}``",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MissingRole):
            missing_role = ctx.guild.get_role(error.missing_role)
            embed = self.embed_gen.get_error_embed(
                title="Missing Role",
                description=f"Sorry, You need to have this role to run this command: ``{missing_role.name}``",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BotMissingRole):
            missing_role = ctx.guild.get_role(error.missing_role)
            embed = self.embed_gen.get_error_embed(
                title="Bot Missing Role",
                description=f"Sorry, I need to have this role to run this command: ``{missing_role.name}``",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MissingAnyRole):
            missing_roles_list = []
            for role in error.missing_roles:
                missing_roles_list.append(ctx.guild.get_role(role))
            missing_roles = ", ".join([role.name for role in missing_roles_list])
            embed = self.embed_gen.get_error_embed(
                title="Missing Any Role",
                description=f"Sorry, You need to have atleast one of these roles to run this command: ``{missing_roles}``",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BotMissingAnyRole):
            missing_roles_list = []
            for role in error.missing_roles:
                missing_roles_list.append(ctx.guild.get_role(role))
            missing_roles = ", ".join([role.name for role in missing_roles_list])
            embed = self.embed_gen.get_error_embed(
                title="Bot Missing Any Role",
                description=f"Sorry, I need to have atleast one of these roles to run this command: ``{missing_roles}``",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.NSFWChannelRequired):
            embed = self.embed_gen.get_error_embed(
                title="NSFW Channel Required",
                description="Sorry, This channel needs to be a nsfw channel in order to run this command.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.UserInputError):
            embed = self.embed_gen.get_error_embed(
                title="Input Error",
                description="Sorry, I failed to parse your input.\nMaybe the command expects a number and you provided a text instead?"
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = self.embed_gen.get_error_embed(
                title="Missing Required Argument",
                description=f"Sorry, You're missing a required argument: ``{error.param.name}``\nMaybe check out the help command?",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ArgumentParsingError):
            embed = self.embed_gen.get_error_embed(
                title="Aurgemnt Parsing error",
                description="Sorry, I failed to parse your argument. Maybe check out the help command?"
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.UnexpectedQuoteError):
            embed = self.embed_gen.get_error_embed(
                title="Unexpected Quote Error",
                description='Sorry, An unexpected quote(") in your input has been detected.\nMaybe check out the help command?',
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.InvalidEndOfQuotedStringError):
            embed = self.embed_gen.get_error_embed(
                title="Invalid End Of Quoted String Error",
                description='Sorry, An empty space was expected after your closing quoted(""<-this) string.\nMaybe check out the help command?',
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ExpectedClosingQuoteError):
            embed = self.embed_gen.get_error_embed(
                title="Expected Closing Quote Error",
                description='Sorry, You started a quoted("") string, But you never closed it.\nMaybe check out the help command?',
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BadArgument):
            embed = self.embed_gen.get_error_embed(
                title="Bad Argument",
                description="Sorry, I failed to convert your input.\nMaybe the command expects a number and you provided a text instead?",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.TooManyArguments):
            embed = self.embed_gen.get_error_embed(
                title="Too Many Arguments",
                description="Sorry, You provided too many arguments to this command.\nMaybe check out the help command?",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CommandOnCooldown):
            embed = self.embed_gen.get_error_embed(
                title="Command On Cooldown",
                description=f"Sorry, This command is on a cooldown.\nPlease wait `{round(error.retry_after, 1)}` more seconds before retrying.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ExtensionError):
            embed = self.embed_gen.get_error_embed(
                title="Extension Error",
                description="Sorry, Failed to load extension.",
            )
            await ctx.send(embed=embed)
            return        

        if isinstance(error, commands.ExtensionAlreadyLoaded):
            embed = self.embed_gen.get_error_embed(
                title="Extension Already Loaded",
                description="Sorry, This Extension is already loaded.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ExtensionNotLoaded):
            embed = self.embed_gen.get_error_embed(
                title="Extension Not Loaded",
                description="Sorry, This Extension is not loaded.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.NoEntryPointError):
            embed = self.embed_gen.get_error_embed(
                title="No Entry Point Error",
                description="Sorry, This Extension does not contain a setup funtion.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ExtensionFailed):
            embed = self.embed_gen.get_error_embed(
                title="Extension Failed",
                description="Sorry, This Extension Failed to load.",
            )
            await ctx.send(embed=embed)

        if isinstance(error, commands.ExtensionNotFound):
            embed = self.embed_gen.get_error_embed(
                title="Extension Not Found",
                description="Sorry, This Extension was not found.",
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MaxConcurrencyReached):
            embed=self.embed_gen.get_error_ember(
                title="Max Concurrency Reached",
                description=f"Sorry, This command can only be used by `{error.number}` user(s) at a time."
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.MessageNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="Message Not Found",
                description="Sorry, The message you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MemberNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="Member Not Found",
                description="Sorry, The member you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.GuildNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="Guild Not Found",
                description="Sorry, The guild you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.UserNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="User Not Found",
                description="Sorry, The user you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ChannelNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="Channel Not Found",
                description="Sorry, The channel you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.RoleNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="Role Not Found",
                description="Sorry, The role you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.EmojiNotFound):
            embed = self.bot.embed_gen.get_error_embed(
                title="Emoji Not Found",
                description="Sorry, The emoji you provided was not found.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ChannelNotReadable):
            embed = self.bot.embed_gen.get_error_embed(
                title="Channel not readable",
                description="Sorry, This channel is not readable by me. Please provide me appropriate permissions.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BadColourArgument):
            embed = self.bot.embed_gen.get_error_embed(
                title="Bad Color Argument",
                description="Sorry, This color is invalid.\nInput: {error.argument}"
            )
            await ctx.send(embed=embed)
            return

        ############################################################################################
        # If error was still not handled

        # If running in dev mode; display the error
        if self.bot.is_env_dev():
            await ctx.send(f"```py\n{error.__class__.__name__}: {str(error)}\n```")
            raise error
            return
        
        # Else dm owner
        embed = self.embed_gen.get_error_embed(
            title="Unexpected Error",
            description="Sorry, An unexpected error occured.\nThis could be a critical error. Bot owner would be notified about this.",
        )
        await ctx.send(embed=embed)

        owner = self.bot.get_user(self.bot.owner_id)
        ctx_dict = f"```py\n{ctx.__dict__}\n```"
        await owner.send(
            f"An error occured in {ctx.guild or 'DM'} while invoking command: {ctx.command.name}\n{error.__class__.__name__}: {str(error)}\n{ctx_dict}"
        )

        raise error

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
