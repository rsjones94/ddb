import discord
from discord.ext import commands
import random

from utils.time import formatToHumanTime

from lib.bot import VoteBot

class Bullying(commands.Cog):
    def __init__(self, bot: VoteBot):
        self.bot = bot
        
        self.user_dict = {
                '855133266071257129':'maria',
                '630126009047318538':'spencer',
                '800050292481065022':'jarrod',
                '712838824782200883':'megan',
                '700051759594471514':'sky',
                '856936371036618793':'ddb'
            }

    @commands.command(name='bully', help='Bullies someone who deserves it.')
    async def bully(self, ctx, user_id):
        
        user = ''.join(c for c in user_id if c.isdigit())
        
        txt = self.get_bully_lines(user)
        
        embedder = discord.Embed(title='BULLYBOT', description=txt, colour=discord.Color.dark_green())
        await ctx.send(embed=embedder)
        
        
    def get_bully_lines(self, user):
        try:
            target = self.user_dict[user]
        except KeyError:
            returner = 'Who are you trying to bully...?'
            return returner
        
        return target

    
def setup(bot: VoteBot):
    bot.add_cog(Bullying(bot))
    
    