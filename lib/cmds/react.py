from collections import defaultdict
from re import search
from datetime import datetime, timedelta
from random import randint
from time import time
import json

from . import db, games, misc

with open('./config.json') as data:
   config = json.load(data)

welcomed = []
messages = defaultdict(int)
#totalmessages = 0

def process(bot, user, message):
   #totalmessages = totalmessages
   if user['id'] != config['streamer']:
      update_records(bot, user)

      if user['id'] not in welcomed:
         welcome(bot, user)
      #elif "bye" in message or "see ya" in message:
         #say_goodbye(bot, user)

      check_activity(bot, user)

      #totalmessages += 1
      #if totalmessages % 50 == 0:
         #misc.discord(bot, user)

      if (match := search(r'cheer[0-9]+', message)) is not None:
         thank_for_cheer(bot, user, match)

      if (h := games.heist) is not None:
         if h.start_time <= time() and not h.running:
            games.run_heist(bot)
         elif h.end_time <= time() and h.running:
            games.end_heist(bot)

def update_records(bot, user):
   db.execute("INSERT OR IGNORE INTO users (UserID) VALUES (?)", user['id'])
   db.execute("UPDATE users SET MessagesSent = MessagesSent + 1 WHERE UserID = ?", user['id'])

   stamp = db.field("SELECT CoinLock FROM users WHERE UserID = ?", user['id'])

   if datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S") < datetime.utcnow():
      coinlock = (datetime.utcnow()+timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")

      db.execute("UPDATE users SET Coins = Coins + ?, CoinLock = ? WHERE UserID = ?", randint(1, 5), coinlock, user['id'])

def welcome(bot, user):
   bot.send_message(f"Welcome to the stream {user['name']}!")
   welcomed.append(user['id'])

def say_goodbye(bot, user):
   bot.send_message(f"See ya later {user['name']}!")
   welcomed.remove(user['id'])

def check_activity(bot, user):
   messages[user['id']] += 1
   count = messages[user['id']]

   if (count % 50 == 0 and count <= 200) or (count % 500 == 0):
      bot.send_message(f"Thanks for being active in chat, {user['name']}. You've sent {count:,} messages! Keep it up!")

def thank_for_cheer(bot, user, match):
   bot.send_message(f"Thanks for the {match[5:]:,} bitties, {user['name']}! It's much appreciated!")