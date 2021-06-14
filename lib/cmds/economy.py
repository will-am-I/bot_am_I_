import MySQLdb, json

with open('./config.json') as data:
   config = json.load(data)

def coins(bot, user, *args):
   db = MySQLdb.connect("localhost", config['database_user'], config['database_pass'], config['database_schema'])
   cursor = db.cursor()
   cursor.execute(f"SELECT coins FROM member_rank WHERE twitchid = {user['id']}")
   coins = cursor.fetchone()[0]
   bot.send_message(f"{user['name']}, you have {coins:,} coins.")

def rank(bot, user, *args):
   pass