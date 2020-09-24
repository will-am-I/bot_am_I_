import urllib.request, json
from datetime import datetime

with open('./config.json') as data:
   config = json.load(data)

def help(bot, prefix, cmds):
   bot.send_message("Registered command: " + ", ".join([f"{prefix}{cmd}" for cmd in sorted(cmds.keys())]))

def hello(bot, user, *args):
   bot.send_message(f"Hello {user['name']}! HeyGuys")

def test(bot, user, *args):
   bot.send_message("Testing, testing 1-2-3")

def discord(bot, user, *args):
   bot.send_message("Join the discord! Keep up with all my speedrunning shenanigans as well as hang out with this goofy bunch at https://discord.gg/HVpSXUk")

def uptime(bot, user, *args):
   url = 'https://api.twitch.tv/helix/streams?user_login=will_am_I_'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   request = urllib.request.Request(url, headers=header)
   with urllib.request.urlopen(request) as streamurl:
      streaminfo = json.loads(streamurl.read().decode())

   if (streaminfo['data']):
      startTime = datetime.strptime(streaminfo['data'][0]['started_at'][:10] + ' ' + streaminfo['data'][0]['started_at'][11:-1], '%Y-%m-%d %H:%M:%S')
      uptime = str(datetime.utcnow() - startTime).rsplit('.', 1)[0]

      bot.send_message(f"Thanks for asking, {user['name']}. Will has been live for {uptime}.")
   else:
      bot.send_message(f"Sorry, {user['name']}, but Will isn't live right now.. obviously..")