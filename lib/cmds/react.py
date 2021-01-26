from collections import defaultdict
from re import search

from . import db

welcomed = []
messages = defaultdict(int)

def process(bot, user, message):
   update_records(bot, user)

   if user['id'] not in welcomed:
      welcome(bot, user)
   elif "bye" in message:
      say_goodbye(bot, user)

   check_activity(bot, user)

   if (match := search(r'cheer[0-9]+', message)) is not None:
      thank_for_cheer(bot, user, match)

def update_records(bot, user):
   db.execute("INSERT OR IGNORE INTO users (UserID) VALUES (?)", user['id'])
   db.execute("UPDATE users SET MessagesSent = MessagesSent + 1 WHERE UserID = ?", user['id'])

def welcome(bot, user):
   bot.send_message(f"Welcome to the stream {user['name']}!")
   welcomed.append(user['id'])

def say_goodbye(bot, user):
   bot.send_message(f"See ya later {user['name']}!")
   welcomed.remove(user['id'])

def check_activity(bot, user):
   messages[user['id']] += 1

   if (count := messages[user['id']]) % 25 == 0:
      bot.send_message(f"Thanks for being active in chat, {user['name']}. You've sent {count:,} messages! Keep it up! PogChamp")

def thank_for_cheer(bot, user, match):
   bot.send_message(f"Thanks for the {match.string[5:]:,} bitties, {user['name']}! It's much appreciated!")