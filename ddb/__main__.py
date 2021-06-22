from dotenv import load_dotenv
load_dotenv()

from lib.bot import VoteBot

if(__name__ == '__main__'):
    bot = VoteBot()
    bot.run()