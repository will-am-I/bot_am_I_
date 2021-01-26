from time import time
from . import misc

PREFIX = "!"

cmds = {
          "hello": misc.hello,
          #"test":  misc.test,
          "discord": misc.discord,
          "uptime": misc.uptime
          #"wr": misc.wr,
          #"pb": misc.pb
       }

def process(bot, user, message):
   if message.startswith(PREFIX):
      cmd = message.split(" ")[0][len(PREFIX):]
      args = message.split(" ")[1:]
      perform(bot, user, cmd, *args)

def perform(bot, user, cmd, *args):
   for name, func in cmds.items():
      if cmd == name:
         func(bot, user, *args)
         return

   if cmd == "help":
      misc.help(bot, PREFIX, cmds)
   else:
      bot.send_message(f"{user['name']}, \"{cmd}\" isn't a registered command. NotLikeThis Type !help for a list of commands.")