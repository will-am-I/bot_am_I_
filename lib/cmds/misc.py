import json, urllib.request

with open('./config.json') as data:
   config = json.load(data)

def help(bot, prefix, cmds, command=None, *args):
   if command is None:
      bot.send_message("Registered commands: " + ", ".join([f"{prefix}{cmd.callables[0]}" for cmd in cmds if cmd != "category"]) + " (type !help <command> for more info on each one)")# in sorted(cmds, key=lambda cmd: cmd.callables[0])]))
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
   #elif command == "heist":
      #bot.send_message("Heist command can be called using !heist <bet>. Enter the number of coins to wager and the heist will start after 1 minute. Anyone may join using !heist <bet> and increase the chances of everyone winning. You will receive 1.5 times what is wagered if you win.")
   elif command == "wr":
      bot.send_message("WR command will display the current world record of the game, category, and possible subcategories of the game Will is currently running.")
   elif command == "pb":
      bot.send_message("PB command will display Will's current personal best time in the game, category, and possible subcategories of the game he is running.")
   elif command == "clip":
      bot.send_message("Clip command will create a clip from the stream.")
   elif command == "dadjoke":
      bot.send_message("Dad Joke command will send a random dad joke.")
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

def dadjoke(bot, user, *args):
   url = "https://www.icanhazdadjoke.com"
   header = {"User-Agent": "will_am_i_", "Accept": "application/json"}
   request = urllib.request.Request(url, headers=header, method="GET")

   with urllib.request.urlopen(request) as jokeinfo:
      joke = json.loads(jokeinfo.read().decode())

   bot.send_message(joke['joke'].replace('\n', ' '))

def play(bot, user, *args):
   if user['id'] == config['streamer']:
      bot.send_message("!play")

def cards(bot, user, *args):
   bot.send_message("Visit https://www.streamloots.com/will_am_i_?couponCode=MVBMN to purchase and redeem playable cards for the stream. The first 5 people get a chest for free!")