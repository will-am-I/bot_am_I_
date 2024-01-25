import twitchio, os
from twitchio.ext import commands, eventsub

eventBot = commands.Bot.from_client_credentials(client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET'])
#eventClient = eventsub.EventSubClient(eventBot,)

class Events(commands.Cog):

   def __init__(self, bot:commands.Bot):
      self.bot = bot

   @commands.Cog.event()
   async def event_command_error(self, ctx:commands.Context, error:Exception):
      print(error.with_traceback)
      await ctx.send("You done messed up A-A-ron!")

def prepare(bot:commands.Bot):
   bot.add_cog(Events(bot))