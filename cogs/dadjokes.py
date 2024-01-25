import urllib.request, json
from twitchio.ext import commands

class DadJoke(commands.Cog):

   def __init__(self, bot:commands.Bot):
      self.bot = bot

   @commands.command()
   async def dadjoke(self, ctx:commands.Context):
      url = "https://www.icanhazdadjoke.com"
      header = {"User-Agent": "will_am_i_", "Accept": "application/json"}
      request = urllib.request.Request(url, headers=header, method="GET")

      with urllib.request.urlopen(request) as jokeinfo:
         joke = json.loads(jokeinfo.read().decode())

      await ctx.send(joke['joke'].replace('\n', ' '))

def prepare(bot:commands.Bot):
   bot.add_cog(DadJoke(bot))