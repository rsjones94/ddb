import discord
from discord.ext import commands
import random
import os
from os import listdir
from os.path import isfile, join


import pandas as pd

from utils.time import formatToHumanTime
from lib.bot import VoteBot

class Tables(commands.Cog):
    def __init__(self, bot: VoteBot):
        self.bot = bot
        
        file = __file__
        parent = os.path.dirname(file)
        pparent = os.path.dirname(parent)
        self.table_folder = os.path.join(pparent, 'tables')

    @commands.command(name='roll',
        description='Rolls nerd dice',
        usage='!roll <number_of_dice>d<number_of_sides>',
        examples=[
            '`!roll 1d20` (rolls a single twenty-sided die)',
            '`!roll 4d8` (rolls 4 eight-sided dice and sums the result)'
        ],
    )
    async def roll(self, ctx, dice_cmd):
        
        split = dice_cmd.split('d')
        n = int(split[0])
        try:
            sides = int(split[1])
        except IndexError:
            sides = 6
        
        dice = [
            str(random.choice(range(1, sides + 1)))
            for _ in range(n)
        ]
        
        res = ', '.join(dice)
        if n > 1:
            dice = [int(d) for d in dice]
            total = int(sum(dice))
            txt = f'{res} =\n{total}'
        else:
            txt = res
        
        embedder = discord.Embed(title=f'Rolling {n}d{sides}', description=txt, colour=discord.Color.dark_green())
        await ctx.send(embed=embedder)

    @commands.command(name='roll-table',
        description='Selects random entries from a table',
        usage='!roll-table <table_name> {number_of_entries}',
        note='If not otherwise specified, selects one entry',
        examples=[
            '`!roll-table lunch` (selects one entry from the table "lunch")',
            '`!roll-table drinks 3` (selects three entries from the table "drinks")'
        ],
    )
    async def roll_table(self, ctx, table_name, num_selections=1):
        the_table = self.load_table(table_name)
        sample = random.sample(the_table, num_selections)
        
        if num_selections == 1:
            sample = sample[0]
        else:
            sample = ', '.join(sample)
        
        embedder = discord.Embed(title=f'Rolling on table "{table_name}"', description=sample, colour=discord.Color.dark_green())
        await ctx.send(embed=embedder)
        
    @commands.command(name='vote-table',
        description='Selects random entries from a table and creates a poll',
        usage='!roll-table <table_name> {number_of_entries}',
        note='If not otherwise specified, selects two entries',
        examples=[
            '`!poll-table lunch` (selects two entries from the table "lunch" and makes a poll)',
            '`!vote-table drinks 3` (selects three entries from the table "drinks" and makes a poll)'
        ],
    )
    async def vote_table(self, ctx, table_name, num_selections=2):
        the_table = self.load_table(table_name)
        sample = random.sample(the_table, num_selections)
        
        
        voter = self.bot.get_cog('Vote')
        await voter._createVote(ctx, table_name, sample, back2list=True)
        
        
        
    @commands.command(name='print-table',
        description='Prints a table in the chat log',
        usage='!print-table <table_name>',
        examples=[
            '`!print-table lunch` (prints the entire table "lunch")'
        ],
    )
    async def print_table(self, ctx, table_name):
        the_table = self.load_table(table_name)
        
        the_output = 'Index, Value'
        i = 0
        for val in the_table:
            the_output = the_output + f'\n{i}, {val}'
            i += 1
        
        embedder = discord.Embed(title=f'Table "{table_name}"', description=the_output, colour=discord.Color.dark_green())
        await ctx.send(embed=embedder)
        
    @commands.command(name='insert-table',
        description='Inserts an entry into a table',
        usage='!insert-table <table_name> <entry_name>',
        examples=[
            '`!insert-table lunch Fido` (inserts the entry "Fido" into the table "lunch")'
        ],
    )
    async def insert_table(self, ctx, table_name, insertion):
        the_table = self.load_table(table_name, as_list=False)
        
        the_table.loc[-1] = insertion # adding a row
        the_table.index = the_table.index + 1  # shifting index
        the_table = the_table.sort_index()  # sorting by index
        
        table_file = os.path.join(self.table_folder, f'{table_name}.csv')
        the_table.to_csv(table_file, header=False, index=False)
         
        await self.print_table(ctx, table_name)
        
    @commands.command(name='list-tables',
        description='Lists all available tables',
        usage='!list-tables'
    )
    async def list_tables(self, ctx):
        csvs = [f[:-4] for f in listdir(self.table_folder) if isfile(join(self.table_folder, f)) and 'csv' in f]
        
        the_output = 'Name, Entries'
        for c in csvs:
            the_list = self.load_table(c)
            n = len(the_list)
            the_output = the_output + f'\n{c}, {n}'
        
        embedder = discord.Embed(title=f'Available tables', description=the_output, colour=discord.Color.dark_green())
        await ctx.send(embed=embedder)
        
    @commands.command(name='pop-table',
        description='Removes an entry from table',
        usage='!insert-table <table_name> <entry_name>',
        examples=[
            '`!pop-table lunch Fido` (removes the entry "Fido" from the table "lunch")'
        ],
    )
    async def pop_table(self, ctx, table_name, drop):
        the_table = self.load_table(table_name, as_list=False)
        the_table = the_table.loc[the_table[0] != drop]
        
        table_file = os.path.join(self.table_folder, f'{table_name}.csv')
        the_table.to_csv(table_file, header=False, index=False)
         
        await self.print_table(ctx, table_name)
        
    @commands.command(name='crush-table',
        description='Destroys an entire table',
        usage='!crush-table <table_name>',
        examples=[
            '`!crush-table lunch` (deletes the table "lunch")'
        ],
    )
    async def crush_table(self, ctx, table_name):
        table_file = os.path.join(self.table_folder, f'{table_name}.csv')
        os.remove(table_file)
         
        await ctx.send(f'Table "{table_name}" is no more')
        
    @commands.command(name='create-table',
        description='Creates a blank table',
        usage='!create-table <table_name>',
        examples=[
            '`!create-table lunch` (creates a blank table called "lunch")'
        ],
    )
    async def create_table(self, ctx, table_name):
        table_file = os.path.join(self.table_folder, f'{table_name}.csv')
        with open(table_file, "w") as my_empty_csv:
            # now you have an empty file already
            pass  # or write something to it already
         
        await ctx.send(f'Table "{table_name}" is born')
        
    @commands.command(name='clone-table',
        description='Creates a copy of a table',
        usage='!clone-table <table_to_copy> <target_name>',
        examples=[
            '`!clone-table lunch dinner` (copies the table "lunch" and saves it as "dinner")'
        ],
    )
    async def clone_table(self, ctx, table_name, target_name):
        the_table = self.load_table(table_name, as_list=False)
        
        table_file = os.path.join(self.table_folder, f'{target_name}.csv')
        the_table.to_csv(table_file, header=False, index=False)
         
        await self.print_table(ctx, target_name)
        
    def load_table(self, table_name, as_list=True):
        table_file = os.path.join(self.table_folder, f'{table_name}.csv')
        
        try:
            the_table = pd.read_csv(table_file, header=None, index_col=False)
        except pd.errors.EmptyDataError:
            the_table = pd.DataFrame(columns=[0])
        
        if as_list:
            the_list = []
            for index, row in the_table.iterrows():
                the_list.append(row[0])
            
            return the_list
        else:
            return the_table
        
        
    
def setup(bot: VoteBot):
    bot.add_cog(Tables(bot))
    
    