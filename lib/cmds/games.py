from random import choice, randint
from time import time
import MySQLdb, json

with open('./config.json') as data:
   config = json.load(data)

heist = None
heist_lock = time()

def coinflip(bot, user, side=None, bet=1, *args):
   db = MySQLdb.connect("localhost", "root", config['database_pass'], config['database_schema'])
   cursor = db.cursor()
   
   try:
      cursor.execute(f"SELECT coins FROM member_points WHERE twitchid = '{user['id']}'")
      if int(cursor.fetchone()) > 0:
         if side is None:
            bot.send_message("Select which side you think the coin will land.")
         elif (side := side.lower()) not in (opt := ("h", "t", "heads", "tails")):
            bot.send_message("Enter one of the following as the side: " + ", ".join(opt))
         else:
            result = choice(("heads", "tails"))
            
            if side[0] == result[0]:
               cursor.execute(f"UPDATE member_points SET coins = coins + {bet} WHERE twitchid = {user['id']}")
               bot.send_message(f"It landed on {result}! You won {bet} coins!")
            else:
               cursor.execute(f"UPDATE member_points SET coins = coins - {bet} WHERE twitchid = {user['id']}")
               bot.send_message(f"Sorry, it landed on {result}. You lost {bet} coin.")
      else:
         bot.send_message(f"Sorry, {user['name']}. You need at least 1 coin to play the coinflip. Participate in chat to earn free coins.")
      db.commit()
   except Exception as e:
      db.rollback()
      bot.send_message("Error occurred during the coinflip.")
      print(str(e))

class Heist(object):
   def __init__(self):
      self.users = []
      self.running = False
      self.start_time = time() + 60
      self.end_time = 0
      self.messages = {
                         "success":
                         [
                            "{} fought off the guards, and got their haul!",
                            "{} sneaked out of the back entrance with their share!",
                            "{} got in and out seemlessly with their money!"
                         ],
                         "failure":
                         [
                            "{} got caught by the guards!",
                            "{} was injured by a gunshot!",
                            "{} got lost!"
                         ],
                      }

   def add_user(self, bot, user, bet):
      if self.running:
         bot.send_message("A Heist is already in progress. You'll have to wait until the next one.")
      elif user in self.users:
         bot.send_message("You're already good to go.")
      #elif bet > (coins := db.field("SELECT Coins FROM users WHERE UserID = ?", user['id'])):
         #bot.send_message(f"You don't have that much to bet. You only have {coins:,} coins.")
      else:
         #db.execute("UPDATE users SET Coins = Coins - ? WHERE UserID = ?", bet, user['id'])
         self.users.append((user, bet))
         bot.send_message("You're all suited and ready to go! Stand by for showtime...")

   def start(self, bot):
      bot.send_message("The heist has started! Standby for results...")
      self.running = True
      self.end_time = time() + randint(30, 60)

   def end(self, bot):
      succeeded = []

      for user, bet in self.users:
         if randint(0, len(self.users)):
            #db.execute("UPDATE users SET Coins = Coins + ? WHERE UserID = ?", bet*1.5, user['id'])
            succeeded.append((user, bet*1.5))
            bot.send_message(choice(self.messages["success"]).format(user['name']))
         else:
            bot.send_message(choice(self.messages["failure"]).format(user['name']))
      
      if len(succeeded) > 0:
         bot.send_message("The heist is over! The winners:" + ", ".join([f"{user['name']} ({coins:,} coins)" for user, coins in succeeded]))
      else:
         bot.send_message("The heist was a failure! No one made it out. Better luck next time!")

def start_heist(bot, user, bet=None, *args):
   global heist

   if bet is None:
      bot.send_message("You need to specify an amount to bet.")
   else:
      try:
         bet = int(bet)
      except ValueError:
         bot.send_message("That's not a valid bet.")
      else:
         if bet < 1:
            bot.send_message("You need to bet at least 1 coin.")
         else:
            if heist is None:
               heist = Heist()
            heist.add_user(bot, user, bet)

def run_heist(bot):
   heist.start(bot)

def end_heist(bot):
   global heist

   heist.end(bot)
   heist = None