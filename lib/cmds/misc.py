import urllib.request, json
from datetime import datetime

with open('./config.json') as data:
   config = json.load(data)

def games(arg):
   switcher = {"New Super Lucky's Tale": "o1y97826",
               "Yooka-Laylee": "m1zz5210",
               "Star Wars: Knights of the Old Republic": "9dokkk1p",
               "Yoku's Island Express": "9dowj231",
               "Lego Island 2 The Brickster's Revenge": "36935g6l"}
   
   return switcher.get(arg, "Unavailable")

def help(bot, prefix, cmds):
   bot.send_message("Registered command: " + ", ".join([f"{prefix}{cmd}" for cmd in sorted(cmds.keys())]))

def hello(bot, user, *args):
   bot.send_message(f"Hello {user['name']}! VoHiYo")

def test(bot, user, *args):
   bot.send_message("Testing, testing 1-2-3")

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

def wr(bot, user, *args):
   bot.send_message("WR")

def pb(bot, user, *args):
   url = 'https://api.twitch.tv/helix/streams?user_login=will_am_i_'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   request = urllib.request.Request(url, headers=header)
   with urllib.request.urlopen(request) as streamurl:
      streaminfo = json.loads(streamurl.read().decode())

   if (streaminfo['data']):
      gameid = streaminfo['data'][0]['game_id']
      request = urllib.request.Request('https://api.twitch.tv/helix/games?id=' + gameid, headers=header)
      with urllib.request.urlopen(request) as gameurl:
         game = json.loads(gameurl.read().decode())['data'][0]['name']

      if (games(game) != "Unavailable"):
         title = streaminfo['data'][0]['title']
         category = title[title.find("{")+1:title.find("}")]
         subcategories = category[category.find("[")+1:category.find("]")].split(",")
         category = category[:category.find("[")-1]
   else:
      bot.send_message("Sorry, Will is offline so there is no game to look for.")