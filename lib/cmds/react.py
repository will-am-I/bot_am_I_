from collections import defaultdict
from re import search
from datetime import datetime, timedelta
from random import randint
from time import time
import json, MySQLdb

from . import games, misc

with open('./config.json') as data:
   config = json.load(data)

messages = defaultdict(int)

def process(bot, user, message):
   if user['id'] != config['streamer']:
      welcome(bot, user)
      update_records(bot, user)
      check_activity(bot, user)

      if (match := search(r'cheer[0-9]+', message)) is not None:
         thank_for_cheer(bot, user, match)

      if (h := games.heist) is not None:
         if h.start_time <= time() and not h.running:
            games.run_heist(bot)
         elif h.end_time <= time() and h.running:
            games.end_heist(bot)

def update_records(bot, user):
   db = MySQLdb.connect("localhost", "root", config['database_pass'], config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute(f"UPDATE twitch_users SET messages = messages + 1 WHERE userid = '{user['id']}'")

      cursor.execute(f"INSERT IGNORE INTO member_rank (twitchid, coins, coinlock) VALUES ('{user['id']}', {randint(1,5)}, NOW())")
      cursor.execute(f"UPDATE member_rank SET points = points + 1 WHERE twitchid = '{user['id']}'")

      cursor.execute(f"SELECT DATE_FORMAT(coinlock, '%Y-%m-%d %T') FROM member_rank WHERE twitchid = '{user['id']}'")
      stamp = cursor.fetchone()
      if datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
         coinlock = (datetime.utcnow() + timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
         cursor.execute(f"UPDATE member_rank SET coins = coins + {randint(1,5)}, coinlock = STR_TO_DATE('{coinlock}', '%Y-%m-%d %T') WHERE twitchid = '{user['id']}'")
      
      db.commit()
   except Exception as e:
      db.rollback()
      bot.send_message("Error occurred updating users.")
      print(str(e))
   
   db.close()

def welcome(bot, user):
   db = MySQLdb.connect("localhost", "root", config['database_pass'], config['database_schema'])
   cursor = db.cursor()

   try:
      bot.send_message(f"Welcome to the stream {user['name']}!")
      
      cursor.execute(f"INSERT IGNORE INTO twitch_users (userid) VALUES ('{user['id']}')")
      cursor.execute(f"UPDATE twitch_users SET welcomed = NOW() WHERE userid = '{user['id']}'")

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

def thank_for_cheer(bot, user, match):
   bot.send_message(f"Thanks for the {match[5:]:,} bitties, {user['name']}! It's much appreciated!")