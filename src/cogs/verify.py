import discord

import typing
import asyncio

from discord.ext import commands

from models import Guild, Config, ConfigType, VerificationMethod
from captcha import Captcha

#TODO: allow users to customize verification method

class Verify(commands.Cog):
    """Main verification"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_gen = bot.embed_gen

    async def get_text_input(self, channel: discord.TextChannel, member_or_user: typing.Union[discord.Member, discord.User], timeout=None) -> discord.Message:
        """Waits for the user for input and returns it"""

        def text_wait_for_check(new_msg: discord.Message):
            return new_msg.author == member_or_user and new_msg.channel == channel

        return await self.bot.wait_for("message", check=text_wait_for_check, timeout=timeout)

    async def verify_text_input(self, captcha: Captcha, input_msg: discord.Message):
        """Verifies user's captcha solve attempt"""

        return await captcha.verify(input_msg.content)

    async def add_verified_role(self, member: discord.Member):
        """Adds the verified role to member verified"""

        guild = member.guild

        guild_obj = await Guild.get(id=guild.id)
        verified_role_id = await Config.get_value_int(guild_obj, ConfigType.VERIFIED_ROLE)
        
        if not verified_role_id: # ignore if not set
            return 

        verified_role = guild.get_role(verified_role_id)
        await member.add_roles(verified_role, reason="Verified User")

        return verified_role

    async def display_captcha(self, captcha_file: discord.File, channel: typing.Union[discord.TextChannel, discord.DMChannel], mention=None):
        """Displays the captcha in an embed"""

        embed = self.embed_gen.get_normal_embed(
            title="Verification Required",
            description="The server you just joined requires manual verification.\n\n**Just reply me with the characters displayed below.**"
        )
        embed.set_image(url="attachment://captcha.png")
        embed.set_footer(text="This prompt will timeout in 60 secs", icon_url=self.bot.user.avatar_url)

        await channel.send(f"{mention or ''}", embed=embed, file=captcha_file)

    async def on_timeout(self, channel: typing.Union[discord.TextChannel, discord.DMChannel], guild: discord.Guild, mention=None):
        """Executes after verification message was timed-out"""

        embed = self.embed_gen.get_error_embed(
            title="Verification Timed Out",
            description="Oops! Seems like you didn't respond in time.\n\nBut, It's fine! You can start the verification process again using the command `verify`"
        )
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="Notice me pls :c")

        await channel.send(f"{mention or ''}", embed=embed)
    
    async def on_fail(self, member_or_user: typing.Union[discord.Member, discord.User], channel: typing.Union[discord.TextChannel, discord.DMChannel], guild: discord.Guild, mention=None):
        """Executes after verification was failed"""

        embed = self.embed_gen.get_warn_embed(
            title="Verification Failed ",
            description="Oh no! That's not the correct answer!\n\n**Would you like to try again?**"
        )
        embed.set_footer(text="Reply back with Y or N", icon_url=self.bot.user.avatar_url)

        await channel.send(f"{mention or ''}", embed=embed)
        
        try:
            reply_msg = await self.bot.wait_for("message", check=lambda m:m.author == member_or_user and m.channel == channel, timeout=60)
        except:
            await self.on_timeout(member_or_user, channel, guild)

        # Dangerous recursion here
        if reply_msg.content.upper() == "Y":
            await self.handle_verification_methods(member_or_user, guild)

        elif reply_msg.content.upper() == "N":
            await channel.send("Bye! You can start the verification process again using the command `verify`")
        else:
            await self.on_fail(member_or_user, channel, guild)


    async def on_success(self, member_or_user: typing.Union[discord.Member, discord.User], channel: typing.Union[discord.TextChannel, discord.DMChannel], guild: discord.Guild, mention=None):
        """Executes after verification was successful"""

        member = guild.get_member(member_or_user.id) # make sure we have a member object

        role = await self.add_verified_role(member)
        
        embed = self.embed_gen.get_normal_embed(
            title="Verification Successful",
            description=f"Good Job! You have been verified!\n\n**I have given you the role `{role}`**"

        )

        await channel.send(f"{mention or ''}", embed=embed)

    async def start_dm_verification(self, member_or_user: typing.Union[discord.Member, discord.User], guild: discord.Guild):
        """Starts verification using DM method"""

        captcha = await Captcha.new(self.bot.CAPTCHA_API_URL, self.bot.aio_session)

        captcha.decode()
        captcha_file = captcha.get_discord_file("captcha.png")

        await self.display_captcha(
            captcha_file,
            (await member_or_user.create_dm())
        )

        try:
            user_input = await self.get_text_input(member_or_user.dm_channel, member_or_user, timeout=60)
        except asyncio.TimeoutError:
            await self.on_timeout(member_or_user, member_or_user.dm_channel, guild)
            return

        result = await self.verify_text_input(captcha, user_input)
        
        if result is False:
            return await self.on_fail(member_or_user, member_or_user.dm_channel, guild)
        
        await self.on_success(member_or_user, member_or_user.dm_channel, guild)

    async def start_channel_verification(self, member: discord.Member, verification_channel: discord.TextChannel):
        """Starts verification using channel method"""

        captcha = await Captcha.new(self.bot.CAPTCHA_API_URL, self.bot.aio_session)

        captcha.decode()
        captcha_file = captcha.get_discord_file("captcha.png")

        await self.display_captcha(
            captcha_file,
            verification_channel,
            mention=member.mention
        )

        try:
            user_input = await self.get_text_input(verification_channel, member, timeout=60)
        except asyncio.TimeoutError:
            await self.on_timeout(member, verification_channel, verification_channel.guild, mention=member.mention)
            return

        result = await self.verify_text_input(captcha, user_input)
        
        if result is False:
            return await self.on_fail(member, verification_channel, verification_channel.guild, mention=member.mention)
        
        await self.on_success(member, verification_channel, verification_channel.guild, mention=member.mention)
        
    async def start_reaction_verification(self, member: discord.Member, guild: discord.Guild):
        """Starts verification using reaction method"""

        pass   

    async def handle_verification_methods(self, member_or_user: typing.Union[discord.Member, discord.User], guild: discord.Guild, invocation_channel: discord.TextChannel=None):
        """Resolves the verification method setting for the guild and verifies accordingly"""

        verification_method = (await Guild.get(id=guild.id)).get_verification_method()

        if verification_method == VerificationMethod.DM:
            if invocation_channel and isinstance(invocation_channel, discord.TextChannel):
                await invocation_channel.send("Starting verification process in DM's...")

            return await self.start_dm_verification(member_or_user, guild)

        if verification_method == VerificationMethod.CHANNEL:

            guild_obj = await Guild.get(id=guild.id)
            verification_channel_id = await Config.get_value_int(guild_obj, ConfigType.VERIFICATION_CHANNEL)

            verification_channel = guild.get_channel(verification_channel_id)
     
            return await self.start_channel_verification(member_or_user, verification_channel)

        await self.start_reaction_verification(member_or_user, guild)

    @commands.Cog.listener(name="on_member_join")
    async def handle_joins(self, member: discord.Member):
        """Starts automatic verification for new members"""

        await self.handle_verification_methods(member, member.guild)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.user) # to prevent spam by same user
    async def verify(self, ctx: commands.Context, guild: discord.Guild=None):
        """Starts the verification process manually"""
 
        if not ctx.guild and not guild:
            await ctx.send("`guild` is a required argument when command is invoked in a DM")
            return

        guild = ctx.guild or guild

        guild_obj = await Guild.get(id=guild.id)
        verified_role_id = await Config.get_value_int(guild_obj, ConfigType.VERIFIED_ROLE)

        if not verified_role_id: # ignore if not set
            return 

        verified_role = guild.get_role(verified_role_id)
        member = guild.get_member(ctx.author.id) # ensure it's a member object

        if verified_role in member.roles:
            await ctx.send("You are already verified!")
            return
        
        await self.handle_verification_methods(ctx.author, guild, invocation_channel=ctx.channel)

def setup(bot: commands.Bot):
    bot.add_cog(Verify(bot))