import os
from twitchio.ext import commands

class Bot(commands.Bot):
   def __init__(self):
      super().__init__(token=os.environ['TMI_TOKEN'], prefix=os.environ['BOT_PREFIX'], initial_channels=[os.environ['CHANNEL']])
      for filename in os.listdir('./cogs'):
         if filename.endswith('.py'):
            self.load_module(f'cogs.{filename[:-3]}')

   async def event_ready(self):
      print('Online')

   async def event_command_error(self, ctx:commands.Context, error:Exception):
         print(error)
         await ctx.send("You done messed up A-A-ron!")

   @commands.command()
   async def load(self, ctx:commands.Context, module:str):
      if ctx.author.id == os.environ['STREAMER_ID']:
         self.load_module(f"cogs.{module}")
         await ctx.send(f"{module} has been loaded.")
         
   @commands.command()
   async def unload(self, ctx:commands.Context, module:str):
      if ctx.author.id == os.environ['STREAMER_ID']:
         self.unload_module(f"cogs.{module}")
         await ctx.send(f"{module} has been unloaded.")
         
   @commands.command()
   async def reload(self, ctx:commands.Context, module:str):
      if ctx.author.id == os.environ['STREAMER_ID']:
         self.unload_module(f"cogs.{module}")
         self.load_module(f"cogs.{module}")
         await ctx.send(f"{module} has been reloaded.")

bot = Bot()
bot.run()