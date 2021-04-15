from time import time

from . import misc, economy, games, speedrun

PREFIX = "!"

class Cmd(object):
   def __init__(self, callables, func, cooldown=0):
      self.callables = callables
      self.func = func
      self.cooldown = cooldown
      self.next_use = time()

cmds = [
          #misc
          Cmd(["hello", "hi", "hey"], misc.hello),
          Cmd(["discord"], misc.discord),
          Cmd(["uptime"], misc.uptime, cooldown=15),
          Cmd(["nsfw"], misc.nsfw),
          #economy
          Cmd(["coins", "money"], economy.coins),
          #Cmd(["rank"], economy.rank),
          #games
          Cmd(["coinflip", "flipcoin", "flip"], games.coinflip, cooldown=30),
          #Cmd(["heist"], games.start_heist, cooldown=300),
          #speedrun
          Cmd(["wr"], speedrun.wr),
          Cmd(["pb"], speedrun.pb),
          Cmd(["category"], speedrun.category),
          #lurk
          Cmd(["lurk"], misc.lurk),
          Cmd(["clearlurk"], misc.clearlurk)
       ]

def process(bot, user, message):
   if message.startswith(PREFIX):
      cmd = message.split(" ")[0][len(PREFIX):]
      args = message.split(" ")[1:]
      perform(bot, user, cmd, *args)

def perform(bot, user, call, *args):
   if call in ("help", "commands", "cmds"):
      misc.help(bot, PREFIX, cmds, *args)
   else:
      for cmd in cmds:
         if call in cmd.callables:
            if time() > cmd.next_use:
               cmd.func(bot, user, *args)
               cmd.next_use = time() + cmd.cooldown
            else:
               bot.send_message(f"Cooldown still in effect. Try again in {cmd.next_use-time():,.0f} seconds.")
            return

      bot.send_message(f"@{user['name']}, \"{call}\" isn't a registered command. NotLikeThis Type !help for a list of commands.")