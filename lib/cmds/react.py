import json
from . import pubsub, eventsub
from pprint import pprint
from uuid import UUID
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope
from twitchAPI.pubsub import PubSub
from twitchAPI.eventsub import EventSub

with open('./config.json') as data:
   config = json.load(data)

def start (bot):
   target_scope = [AuthScope.ANALYTICS_READ_GAMES, AuthScope.BITS_READ, AuthScope.CHANNEL_EDIT_COMMERCIAL, AuthScope.CHANNEL_MANAGE_BROADCAST, AuthScope.CHANNEL_MANAGE_POLLS, AuthScope.CHANNEL_MANAGE_PREDICTIONS, AuthScope.CHANNEL_MANAGE_REDEMPTIONS, AuthScope.CHANNEL_MODERATE, AuthScope.CHANNEL_READ_HYPE_TRAIN, AuthScope.CHANNEL_READ_POLLS, AuthScope.CHANNEL_READ_PREDICTIONS, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_READ_SUBSCRIPTIONS, AuthScope.CHANNEL_SUBSCRIPTIONS, AuthScope.CHAT_EDIT, AuthScope.CHAT_READ, AuthScope.CLIPS_EDIT, AuthScope.MODERATION_READ, AuthScope.USER_EDIT_BROADCAST, AuthScope.USER_MANAGE_BLOCKED_USERS, AuthScope.USER_READ_BLOCKED_USERS, AuthScope.USER_READ_BROADCAST, AuthScope.USER_READ_FOLLOWS, AuthScope.USER_READ_SUBSCRIPTIONS]

   twitch = Twitch(config['client_id'], config['client_secret'])
   twitch.authenticate_app([])
   twitch.set_user_authentication(config['twitch_token'], target_scope, config['refresh_token'])

   def callback_bits (uuid : UUID, data : dict):
      print(f"Got callback for UUID {str(uuid)}")
      print(data)
      pubsub.bits(bot, data['data'])

   def callback_subscriptions (uuid : UUID, data : dict):
      print(f"Got callback for UUID {str(uuid)}")
      print(data)
      pubsub.subscription(bot, data['data'])
      
   def callback_points (uuid : UUID, data : dict):
      print(f"Got callback for UUID {str(uuid)}")
      print(data)
      pubsub.points(bot, data['data'])

   user_id = twitch.get_users(logins=['will_am_i_'])['data'][0]['id']

   pubsubs = PubSub(twitch)
   pubsubs.start()

   bits_uuid = pubsubs.listen_bits(user_id, callback_bits)
   subscriptions_uuid = pubsubs.listen_channel_subscriptions(user_id, callback_subscriptions)
   points_uuid = pubsubs.listen_channel_points(user_id, callback_points)

   #pubsubs.stop()