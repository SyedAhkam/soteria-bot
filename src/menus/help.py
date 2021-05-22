import typing

from discord.ext.menus import ListPageSource, MenuPages
from discord.ext import commands

class BotHelpMenu(ListPageSource):
    """Menu responsible for displaying cogs and their commands"""

    def __init__(self, ctx, cogs: typing.List[commands.Cog], filter_function):
        super().__init__(cogs, per_page=6)
        self.ctx = ctx
        self.filter_function = filter_function

    async def _write_page(self, menu: MenuPages, cogs: typing.List[commands.Cog]):
        embed = self.ctx.bot.embed_gen.get_normal_embed()
        embed.description = f"""
        Use **{self.ctx.prefix}help <category>** to list commands under a category
        Use **{self.ctx.prefix}help <command>** to get detailed help on a single command

        > **Total Categories**: {len(self.ctx.bot.cogs)}
        > **Total Commands**: {len(self.ctx.bot.commands)}
        
        This help message is categorized for easier discoverability of commands. It's intended to give you a bird's-eye view of all the available features.

        *Some commands may be hidden because of permission requirements*
        """
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed.set_author(name='Help', icon_url=self.ctx.bot.user.avatar_url)
        embed.set_thumbnail(
            url=self.ctx.guild.icon_url
            if self.ctx.guild
            else self.ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"Showing {offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} categories",
            icon_url=self.ctx.author.avatar_url,
        )

        for cog in cogs:
            if not (commands := (await self.filter_function(cog.get_commands()))):
                continue

            embed.add_field(
                name=cog.qualified_name.capitalize(),
                value=f"""*{cog.description or 'No Description yet'}*
                `{', '.join(command.name for command in commands if command)}`
                """,
                inline=False,
            )

        return embed

    async def format_page(self, menu: MenuPages, entries: typing.List[commands.Cog]):
        return await self._write_page(menu, entries)

    @staticmethod
    async def start_menu(ctx, cogs, filter_function):
        menu = MenuPages(source=BotHelpMenu(ctx, cogs, filter_function), clear_reactions_after=True, timeout=60)
        await menu.start(ctx)

class CogHelpMenu(ListPageSource):
    """Menu responsible for displaying commands under a cog"""

    def __init__(self, ctx: commands.Context, data: typing.Iterable):
        super().__init__(data, per_page=10)
        self.ctx = ctx

    async def _write_page(self, menu: MenuPages, commands: typing.Iterable[commands.Command]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = self.ctx.bot.embed_gen.get_normal_embed(title="Help", description=commands[0].cog.description)
        embed.set_thumbnail(
            url=self.ctx.guild.icon_url
            if self.ctx.guild
            else self.ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"Showing {offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands",
            icon_url=self.ctx.author.avatar_url,
        )

        for command in commands:
            embed.add_field(
                name=command.name,
                value=command.short_doc or "No help message set",
                inline=False,
            )
        return embed

    async def format_page(self, menu: MenuPages, entries: typing.Iterable[commands.Command]):
        return await self._write_page(menu, entries)

    @staticmethod
    async def start_menu(ctx, commands: typing.Iterable[commands.Command]):
        menu = MenuPages(
                source=CogHelpMenu(ctx, commands),
                clear_reactions_after=True,
                timeout=60.0
            )
        await menu.start(ctx)
