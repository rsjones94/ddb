from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from discord.utils import get

from utils.message import filterReactionCount, getVoteDetails
from utils.time import formatToHumanTime
from utils.constants import REACTIONS

from lib.bot import VoteBot

class Vote(commands.Cog):
    def __init__(self, bot: VoteBot):
        self.bot = bot
        
    @staticmethod
    def canMemberEndPoll(member: discord.Member, message: discord.Message):
        voteDetails = getVoteDetails(message)
        return member.guild_permissions.administrator or voteDetails['author'].name == str(member)

    async def finishVote(self, message: discord.Message):
        reactionsCount = filterReactionCount(message, [*REACTIONS['yesorno'], *REACTIONS['answers']])

        mostVoted = reactionsCount.pop('mostVoted')
        totalVotes = reactionsCount.pop('totalVotes')

        embed = message.embeds[0]
        embed.add_field(name='Most Voted:', value=mostVoted if not mostVoted else ' '.join(mostVoted))
        embed.add_field(name='Total Votes:', value=totalVotes)
        embed.add_field(name='Voting Duration:', value=formatToHumanTime((datetime.utcnow() - embed.timestamp).seconds))

        isWithAnswer = bool(embed.description)

        result = None

        if(not isWithAnswer):
            result = '\n'.join([
                f'{emote} **Votes: {votes}**'
                for emote, votes in reactionsCount.items()
            ])
        else:
            emoteAndAnswer = dict(
                (msg[0], msg)
                for msg in embed.description.split('\n')[:20]
            )

            result = '\n'.join([
                f'{msg} | **Votes: {reactionsCount[emote]}**'
                for emote, msg in emoteAndAnswer.items()
            ])
        
        embed.description = result
        embed.set_footer(text='Voting Finished')
        embed.timestamp = datetime.utcnow()
        await message.clear_reactions()
        await message.edit(embed=embed)

    @commands.command(
        name='vote',
        aliases=['vt', 'v'],
        description='Create a poll',
        usage='p?vote <question> {answers}',
        note='If {answers} is not specified, a YES or No vote will be taken, otherwise, the specified responses will be used.',
        examples=[
            '`p?vote "You like apple?"` (only YES and NO answers)',
            '`p?vote "Which movie to watch?" "Harry Potter" "How To Train Your Dragon" "Don\'t watch"` (With question and answers)'
        ],
    )
    async def _createVote(self, ctx: commands.Context, question: str, *answers: Optional[str]):
        if(len(answers) > 20):
            return await ctx.send(embed=discord.Embed(
                title='Many Answers', description=f'{ctx.author.mention}, the answer limit is 20', colour=discord.Color.dark_red())
            )

        emotesToUse = REACTIONS['yesorno'] if not answers else REACTIONS['answers'][:len(answers)]

        embed = discord.Embed(title=question.title(), colour=discord.Color.purple())
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_footer(text='Voting')
        embed.timestamp = datetime.utcnow()

        if(answers):
            embed.description = '\n'.join([f'{emote} {answer}' for emote, answer in zip(emotesToUse, answers)])

        message = await ctx.send(embed=embed)
        for emote in emotesToUse: await message.add_reaction(emote)

    @commands.command(
        name='endvote',
        aliases=['endv', 'ev'],
        description='Ends a poll by passing the message ID',
        usage='p?endvote <message id>',
        note='You can also end a poll just by reacting with :stop_button: in the poll message'
    )
    async def _endVote(self, ctx: commands.Context, messageId: int):
        message = get(await ctx.channel.history(limit=100).flatten(), id=messageId)

        if(not message):
            return await ctx.send(f'Not found a message with ID: {messageId}')

        elif(not self.canMemberEndPoll(ctx.author, message)):
            return await ctx.send('You cannot end this poll')

        elif(message.author.id != self.bot.user.id):
            return await ctx.send('The message needs to be mine, not someone else\'s')

        elif(not message.embeds):
            return await ctx.send('The wrong message, it has to be with Embed')

        elif(not 'Voting' in str(message.embeds[0].footer)):
            return await ctx.send('Wrong message, this is not the vote')

        elif('Voting Finished' in str(message.embeds[0].footer)):
            return await ctx.send('This poll has already ended')

        await self.finishVote(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if(
            payload.member.bot or \
            not payload.member.guild_permissions.administrator or \
            not payload.emoji.name in REACTIONS['finish']
        ): return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = get(await channel.history(limit=100).flatten(), id=payload.message_id)

        if(
            message.author.id == self.bot.user.id and \
            message.embeds and \
            'Voting' in str(message.embeds[0].footer) and \
            not 'Voting Finished' in str(message.embeds[0].footer) and \
            self.canMemberEndPoll(payload.member, message)
        ):
            await self.finishVote(message)
            

def setup(bot: VoteBot):
    bot.add_cog(Vote(bot))