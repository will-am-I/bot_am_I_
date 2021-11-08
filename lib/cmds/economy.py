import mysql.connector, json

with open('./config.json') as data:
   config = json.load(data)

def coins(bot, user, *args):
   db = mysql.connector.connect(host="localhost", user=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()
   cursor.execute(f"SELECT coins FROM member_rank WHERE twitchid = {user['id']}")
   coins = cursor.fetchone()[0]
   bot.send_message(f"{user['name']}, you have {coins:,} coins.")

def rank(bot, user, *args):
   pass