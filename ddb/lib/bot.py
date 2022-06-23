import os
import traceback
import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from utils.constants import COMMANDS_PATH

intents = discord.Intents().default()
intents.members = True

class VoteBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            description='Our lab bot <3',
            help_command=None,
            case_insensitive=True,
            loop=asyncio.get_event_loop(),
            intents=intents,
        )

        self.version = '0.0.1'
        self.loadExtensions()

    async def sendMessageToOwner(self, *, content: str = None, embed: discord.Embed = None):
        await self.info.owner.send(content, embed=embed)

    def loadExtensions(self, extensionsPath: str = 'commands.'):
        extensions = [filename[:-3] for filename in os.listdir(COMMANDS_PATH) if filename.endswith('.py') and not filename.startswith('_')]

        for extension in extensions: self.load_extension(f'{extensionsPath}{extension}')
           
    
    async def on_error(self, event, *args, **kwargs):
        print('Encountered an error...')
        if(self.dev):
            print('Dev')
            traceback.print_exc()
        else:
            embed = discord.Embed(
                title=':x: Event Error',
                description='```py\n%s\n```' % traceback.format_exc(),
                colour=discord.Color.dark_red()
            )
            embed.add_field(name='Event', value=event)
            embed.timestamp = datetime.utcnow()

            try:
                await self.info.owner.send(embed=embed)
            except Exception as e:
                print('Could not log error to owner')
                print(e)
                pass

    async def on_command_error(self, ctx, error):
        if(isinstance(error, commands.MissingRequiredArgument)):
            req_arg = discord.Embed(
                title="Missing Required Argument",
                description=f"{ctx.author.mention}, `<{error.param.name}>` is a required argument",
                color=discord.Color.dark_red())
            return await ctx.channel.send(embed=req_arg)

        elif(isinstance(error, commands.MissingPermissions)):
            missing = discord.Embed(
                title="Insufficient User Permissions",
                description=f"{ctx.author.mention}, to execute this command, you need `{'` `'.join(error.missing_perms).replace('_', ' ').title()}`",
                color=discord.Color.dark_red())
            return await ctx.channel.send(embed=missing)

        elif(isinstance(error, commands.BotMissingPermissions)):
            missing = discord.Embed(
                title="Insufficient Bot Permissions",
                description=f"{ctx.author.mention}, to execute this command, I need `{'` `'.join(error.missing_perms).replace('_', ' ').title()}`",
                color=discord.Color.dark_red())
            return await ctx.channel.send(embed=missing)

        elif(isinstance(error, commands.NotOwner)):
            not_owner = discord.Embed(
                title="Insufficient User Permissions",
                description=f"{ctx.author.mention}, only the bot owner is authorised to use this command",
                color=discord.Color.dark_red())
            return await ctx.channel.send(embed=not_owner)

        elif(isinstance(error, commands.CheckFailure)): pass

        elif(isinstance(error, commands.CommandNotFound)): pass

        else:
            if(self.dev):
                raise error
            else:
                embed = discord.Embed(
                    title=':x: Command Error',
                    colour=discord.Color.dark_red()
                )
                embed.add_field(name='Guild', value=ctx.guild)
                embed.add_field(name='Channel', value=ctx.channel)
                embed.add_field(name='User', value=ctx.author)
                embed.add_field(name='Message', value=ctx.message.clean_content)
                embed.add_field(name='Error', value=error, inline=False)
                embed.timestamp = datetime.utcnow()

                try:
                    self.loop.create_task(self.sendMessageToOwner(embed=embed))
                except:
                    pass

    async def on_ready(self):
        self.dev = self.user.id == 616115002243547196
        self.info = await self.application_info()

        self.startedAt = datetime.now()

        readyMessage = f'{self.user} are online!'
        print(readyMessage)

        if(not self.dev): await self.loop.create_task(self.sendMessageToOwner(content=readyMessage))

    def run(self):
        super().run(os.environ.get('DISCORD_TOKEN'))
