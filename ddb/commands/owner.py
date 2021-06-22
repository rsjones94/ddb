from datetime import datetime

import discord
from discord.ext import commands

from utils.time import formatToHumanTime

from lib.bot import VoteBot

class Owner(commands.Cog):
    def __init__(self, bot: VoteBot):
        self.bot = bot

    @commands.command(
        aliases=['sts'],
        description='Bot status',
        usage='p?stats'
    )
    @commands.is_owner()
    async def stats(self, ctx: commands.Context):
        embed = discord.Embed(
            title='⚙ Bot Stats',
            description=f'🕑 Bot is online in {formatToHumanTime((datetime.now() - self.bot.startedAt).seconds)}',
            colour=discord.Color.purple()
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=f'Version: {self.bot.version} | {int(self.bot.latency*1000)}ms')

        embed.add_field(name='Servers:', value=len(self.bot.guilds))
        embed.add_field(name='Members:', value=len(list(self.bot.get_all_members())))

        await ctx.send(embed=embed)

    @commands.command(
        name='loadextension',
        aliases=['load', 'ld'],
        description='Load an extension',
        usage='p?loadextension <extension>'
    )
    @commands.is_owner()
    async def _loadExtension(self, ctx: commands.Context, extension: str):
        try:
            await self.bot.load_extension(f'commands.{extension}')
        except(commands.ExtensionNotFound):
            await ctx.send(embed=discord.Embed(title='Extension not found', colour=discord.Color.dark_red()))
        except(commands.ExtensionAlreadyLoaded):
            await ctx.send(embed=discord.Embed(title='Extension is already loaded', colour=discord.Color.dark_red()))
        except(commands.ExtensionError):
            await ctx.send(embed=discord.Embed(title='Failed to load extension', colour=discord.Color.dark_red()))
        else:
            await ctx.send(embed=discord.Embed(title='Extension successfully loaded', colour=discord.Color.green()))
    
    @commands.command(
        name='unloadextension',
        aliases=['unload', 'uld'],
        description='Unload an extension',
        usage='p?unloadextension <extension>'
    )
    @commands.is_owner()
    async def _unloadExtension(self, ctx: commands.Context, extension: str):
        try:
            await self.bot.unload_extension(f'commands.{extension}')
        except(commands.ExtensionNotFound):
            await ctx.send(embed=discord.Embed(title='Extension not found', colour=discord.Color.dark_red()))
        except(commands.ExtensionNotLoaded):
            await ctx.send(embed=discord.Embed(title='Failed to load extension', colour=discord.Color.dark_red()))
        except(commands.ExtensionError):
            await ctx.send(embed=discord.Embed(title='Error to load extension', colour=discord.Color.dark_red()))
        else:
            await ctx.send(embed=discord.Embed(title='Extension successfully unloaded', colour=discord.Color.green()))
    
    @commands.command(
        name='reloadextension',
        aliases=['reload', 'rld'],
        description='Reload an extension',
        usage='p?reloadextension <extension>'
    )
    @commands.is_owner()
    async def _unloadExtension(self, ctx: commands.Context, extension: str):
        try:
            await self.bot.reload_extension(f'commands.{extension}')
        except(commands.ExtensionNotFound):
            await ctx.send(embed=discord.Embed(title='Extension not found', colour=discord.Color.dark_red()))
        except(commands.ExtensionError):
            await ctx.send(embed=discord.Embed(title='Error to load extension', colour=discord.Color.dark_red()))
        else:
            await ctx.send(embed=discord.Embed(title='Extension successfully unloaded', colour=discord.Color.green()))

def setup(bot: VoteBot):
    bot.add_cog(Owner(bot))