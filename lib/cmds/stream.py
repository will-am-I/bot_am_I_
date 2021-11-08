import json, mysql.connector
from datetime import datetime, timedelta
from time import time, sleep
from urllib import request, parse

with open('./config.json') as data:
   config = json.load(data)

def uptime(bot, user, *args):
   url = 'https://api.twitch.tv/helix/streams?user_login=will_am_i_'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   with request.urlopen(request.Request(url, headers=header, method="GET")) as streamurl:
      streaminfo = json.loads(streamurl.read().decode())

   if (streaminfo['data']):
      startTime = datetime.strptime(streaminfo['data'][0]['started_at'][:10] + ' ' + streaminfo['data'][0]['started_at'][11:-1], '%Y-%m-%d %H:%M:%S')
      uptime = str(datetime.utcnow() - startTime).rsplit('.', 1)[0]

      bot.send_message(f"Thanks for asking, {user['name']}. Will has been live for {uptime}.")
   else:
      bot.send_message(f"Sorry, {user['name']}, but Will isn't live right now.. obviously.. ResidentSleeper")

def game (bot, user, *args):
   url = 'https://api.twitch.tv/helix/streams?user_login=will_am_i_'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   with request.urlopen(request.Request(url, headers=header, method="GET")) as streamurl:
      streaminfo = json.loads(streamurl.read().decode())

   if streaminfo['data']:
      gameid = streaminfo['data'][0]['game_id']
      with request.urlopen(request.Request('https://api.twitch.tv/helix/games?id=' + gameid, headers=header, method="GET")) as gameurl:
         gameinfo = json.loads(gameurl.read().decode())['data'][0]
      game = gameinfo['name']

      bot.send_message(f"Will is playing {game}.")
   else:
      bot.send_message(f"Sorry, {user['name']}, but Will isn't live right now.. obviously.. ResidentSleeper")

def clip(bot, user, *args):
   url = 'https://api.twitch.tv/helix/clips?broadcaster_id=158745134'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   with request.urlopen(request.Request(url, headers=header, method="POST")) as createjson:
      createinfo = json.loads(createjson.read().decode())

   clip_created = False
   clip_id = createinfo['data'][0]['id']
   clip_url = ""
   clip_start = datetime.now()
   while (datetime.now() - timedelta(seconds=15) <= clip_start and not clip_created):
      url = f"https://api.twitch.tv/helix/clips?id={clip_id}"
      header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
      with request.urlopen(request.Request(url, headers=header, method="GET")) as clipjson:
         clipinfo = json.loads(clipjson.read().decode())

      if clipinfo['data']:
         clip_created = True
         clip_url = clipinfo['data'][0]['url']
      sleep(2)

   if clip_created:
      bot.send_message(clip_url)
   else:
      bot.send_message("Clip creation failed, please try again or create one manually.")

def lurk(bot, user, *args):
   db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute(f"UPDATE twitch_users SET lurking = 'Y' WHERE userid = {user['id']}")
      db.commit()
   except Exception as e:
      db.rollback()
      bot.send_message("Error occurred setting the lurking status.")
      print(str(e))
   else:
      bot.send_message(f"Thanks for lurking {user['name']}! You can still receive points and coins now.")

   db.close()

def clearlurk(bot, user, *args):
   if user['id'] == config['streamer']:
      db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
      cursor = db.cursor()

      try:
         cursor.execute("UPDATE twitch_users SET lurking = 'N' WHERE lurking = 'Y'")
         db.commit()
      except Exception as e:
         db.rollback()
         bot.send_message("Error occurred clearing lurkers.")
         print(str(e))
      else:
         bot.send_message("All lurkers cleared.")

      db.close()