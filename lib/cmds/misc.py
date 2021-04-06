import urllib.request, json
from datetime import datetime

with open('./config.json') as data:
   config = json.load(data)

def help(bot, prefix, cmds, command=None, *args):
   if command is None:
      bot.send_message("Registered commands: " + ", ".join([f"{prefix}{cmd.callables[0]}" for cmd in cmds]) + " (type !help <command> for more info on each one)")# in sorted(cmds, key=lambda cmd: cmd.callables[0])]))
   elif command == "hello":
      bot.send_message("Hello command can be called using !hello, !hi, or !hey. I will simply say hello back.")
   elif command == "discord":
      bot.send_message("Discord command posts a link to Will's discord server.")
   elif command == "uptime":
      bot.send_message("Uptime command displays how long Will has been live.")
   elif command == "coins":
      bot.send_message("Coins command will tell you how many coins you have.")
   elif command == "coinflip":
      bot.send_message("Coinflip command can be called with !coinflip, !flipcoin, or !flip followed by \"heads\" (or 'h') or \"tails\" (or 't'), for example (!coinflip tails). It costs 1 coin to play and you win 10 if you guess correctly.")
   elif command == "heist":
      bot.send_message("Heist command can be called using !heist <bet>. Enter the number of coins to wager and the heist will start after 1 minute. Anyone may join using !heist <bet> and increase the chances of everyone winning. You will receive 1.5 times what is wagered if you win.")
   elif command == "wr":
      bot.send_message("WR command will display the current world record of the game, category, and possible subcategories of the game Will is currently running.")
   elif command == "pb":
      bot.send_message("PB command will display Will's current personal best time in the game, category, and possible subcategories of the game he is running.")
   else:
      bot.send_message("That is not a known command.")

def hello(bot, user, *args):
   bot.send_message(f"Hello {user['name']}! VoHiYo")

def test(bot, user, *args):
   bot.send_message("Testing, testing 1-2-3")

def nsfw(bot, user, *args):
   bot.send_message("Check this out ;) https://matias.ma/nsfw/")

def discord(bot, user, *args):
   bot.send_message("Join the discord! Keep up with all my speedrunning shenanigans as well as hang out with this goofy bunch at https://discord.gg/HVpSXUk")

def uptime(bot, user, *args):
   url = 'https://api.twitch.tv/helix/streams?user_login=will_am_i_'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   request = urllib.request.Request(url, headers=header)
   with urllib.request.urlopen(request) as streamurl:
      streaminfo = json.loads(streamurl.read().decode())

   if (streaminfo['data']):
      startTime = datetime.strptime(streaminfo['data'][0]['started_at'][:10] + ' ' + streaminfo['data'][0]['started_at'][11:-1], '%Y-%m-%d %H:%M:%S')
      uptime = str(datetime.utcnow() - startTime).rsplit('.', 1)[0]

      bot.send_message(f"Thanks for asking, {user['name']}. Will has been live for {uptime}.")
   else:
      bot.send_message(f"Sorry, {user['name']}, but Will isn't live right now.. obviously.. ResidentSleeper")