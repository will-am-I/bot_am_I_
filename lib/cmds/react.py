from collections import defaultdict
from re import search
from datetime import datetime, timedelta
from random import randint
from time import time
import json, mysql.connector, urllib.request

from . import games

with open('./config.json') as data:
   config = json.load(data)

messages = defaultdict(int)

def process(bot, user, message):
   #print(user)
   if user['id'] != config['streamer']:
      welcome(bot, user)
      update_records(bot, user)
      check_activity(bot, user)
      check_timed_messages(bot)

      if (match := search(r'cheer[0-9]+', message)) is not None:
         thank_for_cheer(bot, user, match)

      if (h := games.heist) is not None:
         if h.start_time <= time() and not h.running:
            games.run_heist(bot)
         elif h.end_time <= time() and h.running:
            games.end_heist(bot)
   else:
      update_records(bot, user)

def update_records(bot, user):
   db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute(f"UPDATE twitch_users SET messages = messages + 1 WHERE userid = {user['id']}")

      cursor.execute(f"SELECT * FROM member_rank WHERE twitchid = {user['id']}")
      _ = cursor.fetchall()

      if cursor.rowcount > 0:
         print("existing member")
         cursor.execute(f"UPDATE member_rank SET points = points + 1 WHERE twitchid = {user['id']}")
      else:
         print("new member")
         cursor.execute(f"INSERT INTO member_rank (twitchname, twitchid, points, coins, coinlock) VALUES ('{user['name']}', {user['id']}, 1, {randint(1,5)}, NOW())")

      cursor.execute(f"SELECT DATE_FORMAT(coinlock, '%Y-%m-%d %T') FROM member_rank WHERE twitchid = {user['id']}")
      stamp = cursor.fetchone()[0]
      if datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
         coinlock = (datetime.utcnow() + timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
         cursor.execute(f"UPDATE member_rank SET coins = coins + {randint(1,5)}, coinlock = STR_TO_DATE('{coinlock}', '%Y-%m-%d %T') WHERE twitchid = {user['id']}")
      
      db.commit()
   except Exception as e:
      db.rollback()
      bot.send_message("Error occurred updating users.")
      print(str(e))
   
   db.close()

def welcome(bot, user):
   db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute(f"SELECT * FROM twitch_users WHERE userid = {user['id']}")
      _ = cursor.fetchall()

      if cursor.rowcount > 0:
         url = 'https://api.twitch.tv/helix/streams?user_login=will_am_i_'
         header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
         request = urllib.request.Request(url, headers=header, method="GET")
         with urllib.request.urlopen(request) as streamurl:
            streaminfo = json.loads(streamurl.read().decode())
         if (streaminfo['data']):
            startTime = datetime.strptime(streaminfo['data'][0]['started_at'][:10] + ' ' + streaminfo['data'][0]['started_at'][11:-1], '%Y-%m-%d %H:%M:%S')
         
            cursor.execute(f"SELECT DATE_FORMAT(welcomed, '%Y-%m-%d %T') FROM twitch_users WHERE userid = {user['id']}")
            stamp = datetime.strptime(cursor.fetchone()[0], '%Y-%m-%d %H:%M:%S')
            
            if stamp < startTime:
               bot.send_message(f"Welcome to the stream {user['name']}!")
               cursor.execute(f"UPDATE twitch_users SET welcomed = UTC_TIMESTAMP WHERE userid = {user['id']}")
      else:
         cursor.execute(f"INSERT INTO twitch_users (userid, welcomed) VALUES ({user['id']}, UTC_TIMESTAMP)")
         bot.send_message(f"Welcome to the stream {user['name']}!")

      db.commit()
   except Exception as e:
      db.rollback()
      bot.send_message("Error occurred welcoming users.")
      print(str(e))

   db.close()

def check_activity(bot, user):
   messages[user['id']] += 1
   count = messages[user['id']]

   if (count % 50 == 0 and count <= 200) or (count % 500 == 0):
      bot.send_message(f"Thanks for being active in chat, {user['name']}. You've sent {count:,} messages! Keep it up!")

def check_timed_messages(bot):
   db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute(f"SELECT messageid, message, messages, min_messages, min_time, DATE_FORMAT(last_sent, '%Y-%m-%d %T') FROM timed_messages")
      messages = cursor.fetchall()

      for message in messages:
         if datetime.now() - timedelta(minutes=message[4]) > datetime.strptime(message[5], '%Y-%m-%d %H:%M:%S') and message[2] >= message[3]:
            bot.send_message(str(message[1]))
            cursor.execute(f"UPDATE timed_messages SET messages = 0, last_sent = CURRENT_TIMESTAMP WHERE messageid = {message[0]}")
         else:
            cursor.execute(f"UPDATE timed_messages SET messages = messages + 1 WHERE messageid = {message[0]}")

      db.commit()
   except Exception as e:
      db.rollback()
      bot.send_message("Error occured checking on timed messages.")
      print(str(e))

   db.close()

def thank_for_cheer(bot, user, match):
   bot.send_message(f"Thanks for the {match[5:]:,} bitties, {user['name']}! It's much appreciated!")