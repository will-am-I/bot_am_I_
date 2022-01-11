import json

with open('./config.json') as data:
   config = json.load(data)

def bits (bot, data):
   message = json.load(data['message'])['data']

   if message['is_anonymous'] == True:
      bot.send_message(f"Thank you, random citizen, for the {message['bits_used']} bits!")
   else:
      if int(message['bits_used']) < int(message['total_bits_used']):
         bot.send_message(f"Thank you, {message['user_name']}, for the {message['bits_used']} bits! That's a grand total of {message['total_bits_used']}! PogChamp")
      else:
         bot.send_message(f"Thank you, {message['user_name']}, for the {message['bits_used']} bits! PogChamp")

def subscription (bot, data):
   pass

def points (bot, data):
   redemption = data['redemption']
   title = redemption['reward']['title']
   user = redemption['user']['display_name']

   if title == "Hi!":
      bot.send_message(f"Hello {user}! VoHiYo")