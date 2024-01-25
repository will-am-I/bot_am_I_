import os
from twitchio.ext import commands

class Bot(commands.Bot):
   def __init__(self):
      super().__init__(token=os.environ['TMI_TOKEN'], prefix=os.environ['BOT_PREFIX'], initial_channels=[os.environ['CHANNEL']])
      for filename in os.listdir('./cogs'):
         if filename.endswith('.py'):
            self.load_module(f'cogs.{filename[:-3]}')

   async def event_ready(self):
      print(f'Logged in as | {self.nick}')
      print(f'User id is | {self.user_id}')

   async def event_message(self, message):
      if message.echo:
         return
      
      print(message.content)
      await self.handle_commands(message)

   @commands.command()
   async def hello(self, ctx:commands.Context):
      await ctx.send(f'Hello, {ctx.author.name}!')

bot = Bot()
bot.run()