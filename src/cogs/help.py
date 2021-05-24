import typing

from discord.ext import commands

from menus.help import BotHelpMenu, CogHelpMenu


class HelpCommand(commands.HelpCommand):
    """Custom help command"""

    def __init__(self):
        super().__init__(verify_checks=True)
        self.ignored_cogs = "Help"

    def filter_cogs(self, cogs: typing.List[commands.Cog]):
        """Filters cogs and removes ignored cogs"""
        return [
            cog for cog in cogs if cog and (cog.qualified_name not in self.ignored_cogs)
        ]

    async def send_bot_help(
        self,
        mapping: typing.Mapping[
            typing.Optional[commands.Cog], typing.List[commands.Command]
        ],
    ):
        """Sends bot help message"""

        all_cogs = list(mapping.keys())

        cogs_filtered = self.filter_cogs(all_cogs)

        await BotHelpMenu.start_menu(self.context, cogs_filtered, self.filter_commands)

    async def send_cog_help(self, cog: commands.Cog):
        """Sends cog help message"""

        all_cog_commands = cog.get_commands()
        filtered_commands = await self.filter_commands(all_cog_commands)

        if not filtered_commands:
            await self.get_destination().send("This category contains no commands.")
            return

        await CogHelpMenu.start_menu(self.context, filtered_commands)

    async def send_command_help(self, command: commands.Command):
        """Sends command help message"""

        embed = self.context.bot.embed_gen.get_normal_embed(
            title="Help",
            description=command.help or "No help message",
        )

        embed.set_thumbnail(
            url=self.context.guild.icon_url
            if self.context.guild
            else self.context.author.avatar_url
        )

        embed.add_field(name="Name:", value=command.name, inline=False)
        embed.add_field(
            name="Category:", value=command.cog.qualified_name, inline=False
        )
        embed.add_field(
            name="Aliases:", value=(", ".join(command.aliases)) or "None", inline=False
        )
        embed.add_field(
            name="Usage:", value=self.get_command_signature(command), inline=False
        )

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        """Sends group help message"""

        embed = self.context.bot.embed_gen.get_normal_embed(
            title="Help",
            description=f"""{group.help or 'No help message yet'}
            
            This command is a group and contain subcommands.
            Help for those can be accessed like: `{self.context.prefix}help {group.name} <subcommand>`
            """,
        )

        embed.set_thumbnail(
            url=self.context.guild.icon_url
            if self.context.guild
            else self.context.author.avatar_url
        )

        embed.add_field(name="Name:", value=group.name, inline=False)
        embed.add_field(name="Category:", value=group.cog.qualified_name, inline=False)
        embed.add_field(
            name="Aliases:", value=(", ".join(group.aliases)) or "None", inline=False
        )
        embed.add_field(
            name="Subcommands:",
            value=f"`{', '.join(command.name for command in group.commands)}`"
            if group.commands
            else "None",
        )
        embed.add_field(
            name="Usage:",
            value=self.get_command_signature(group) or "None",
            inline=False,
        )

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        """Sends the error message"""

        await self.get_destination().send(error)

    def command_not_found(self, command_name: str):
        """Returns a string of error message when a command is not found"""

        return f"No command called {command_name} exists."

    def subcommand_not_found(
        self, main_command: commands.Command, subcommand_name: str
    ):
        """Returns a string of error message when a subcommand is not found"""
        if not len(main_command.commands):
            return f'Command "{main_command.qualified_name}" has no subcommands.'

        return f'No subcommand called "{subcommand_name}" exists for command {main_command.qualified_name}.'


class Help(commands.Cog):
    """Help cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Bind help command to cog
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        """Restore the original command after cog unload"""

        self.bot.help_command = self._original_help_command


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
