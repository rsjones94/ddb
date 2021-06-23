from typing import Optional
from datetime import datetime

import discord
from discord.ext import commands

from lib.bot import VoteBot

class Public(commands.Cog):
    def __init__(self, bot: VoteBot):
        self.bot = bot
        self.allowedCogs = ['Vote', 'Help']
        
    async def dispatch(self, ctx: commands.Context, command: commands.Command):
        kwargs = command.__original_kwargs__
        embed = discord.Embed(
            title=f'Details of {command.name.title()}',
            description=kwargs['description'],
            colour=discord.Color.purple()
        )
        embed.set_footer(text='<> is required, {} is optional')

        embed.add_field(name='Usage:', value=command.usage, inline=False)
        for attr in [key for key in kwargs.keys() if not key in ['name', 'description', 'usage', 'invoke_without_command']]:
            if(attr == 'aliases'):
                name, value = attr.title(), ', '.join([alias for alias in command.aliases if alias != command.name.lower()])
            elif(attr == 'note'):
                name, value = attr.title(), f'**{kwargs[attr]}**'
            elif(attr == 'examples'):
                name, value = attr.title(), '\n'.join(kwargs[attr])
            else:
                name, value = attr.title(), kwargs[attr]
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        aliases=['h'],
        description='The help command for the help command',
        usage='!help {command}',
        note='If {command} is specified, it will show the detailed help for that command'
    )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def help(self, ctx: commands.Context, commandName: Optional[str]):
        if(commandName):
            command = self.bot.get_command(commandName)
            if(not command):
                return await ctx.send(embed=discord.Embed(title='Command Not Found', colour=discord.Color.dark_red()))
            
            return await self.dispatch(ctx, command)

        embed = discord.Embed(
            title='VoteBot Help Menu',
            description='For more details on the command, type `!help {command}`',
            colour=discord.Color.purple()
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_field(name='Commands:', value='\n'.join([
            f'> **{command.name}**' for command in self.bot.commands
            if(
                ((authorId := ctx.author.id) == (ownerId := self.bot.info.owner.id)) or \
                ((authorId != ownerId) and command.cog_name in self.allowedCogs)
            )
        ]))

        await ctx.send(embed=embed)

    @commands.command(
        name='bug',
        aliases=['b'],
        description='Report a bug',
        usage='!bug <report>',
        cooldown='30 seconds'
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def _bugReport(self, ctx: commands.Context, *, report: str):
        embed = discord.Embed(title='🛠 Bug Report', colour=discord.Color.purple())
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f'ID: {ctx.author.id}')
        embed.timestamp = datetime.utcnow()
        
        embed.add_field(name='Report:', value=report)

        try:
            await self.bot.info.owner.send(embed=embed)
        except(discord.HTTPException):
            await ctx.send(embed=discord.Embed(title='Failed to Report', colour=discord.Color.dark_red()))
        else:
            await ctx.send(embed=discord.Embed(
                title='🌟 Successfully reported',
                description='Thank you for reporting an error!',
                colour=discord.Color.green()
            ))

    @commands.command(
        name='suggestion',
        aliases=['sug'],
        description='Send a suggestion or idea you have that could be interesting for the bot',
        usage='!suggestion <seggestion>',
    )
    async def _anSuggestion(self, ctx: commands.Context, *, suggestion: str):
        embed = discord.Embed(title='🗨 Suggestion', colour=discord.Color.purple())
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f'ID: {ctx.author.id}')
        embed.timestamp = datetime.utcnow()
        
        embed.add_field(name='Suggestion:', value=suggestion)

        try:
            await self.bot.info.owner.send(embed=embed)
        except(discord.HTTPException):
            await ctx.send(embed=discord.Embed(title='Failed to send suggestion', colour=discord.Color.dark_red()))
        else:
            await ctx.send(embed=discord.Embed(
                title='🌟 Suggestion sent successfully',
                description='Thanks for submitting the suggestion!!',
                colour=discord.Color.green()
            ))

def setup(bot: VoteBot):
    bot.add_cog(Public(bot))