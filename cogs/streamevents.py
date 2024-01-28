import twitchio, os
from twitchio.ext import commands, eventsub

class StreamEvents(commands.Cog):

   def __init__(self, bot:commands.Bot):
      self.bot = bot
      self.eventClient = eventsub.EventSubWSClient(self.bot)
      self.bot.loop.create_task(self.sub())

   async def event_eventsub_notification_followV2(self, event:eventsub.ChannelFollowData):
      print(event)
      print(f"{event.user.name} dropped a follow.")

   async def event_eventsub_notification_subscription(self, event:eventsub.ChannelSubscribeData):
      print(event)
      if not event.is_gift:
         print(f"Got subscription from {event.user.name}")
         await event.broadcaster.channel.send(f"Thanks {event.user.name} for the Tier {event.tier} subscription!")

   async def sub(self):
      await self.eventClient.subscribe_channel_follows_v2(broadcaster=os.environ['STREAMER_ID'], moderator=os.environ['MODERATOR_ID'], token=os.environ['TWITCH_TOKEN'])
      await self.eventClient.subscribe_channel_subscriptions(broadcaster=os.environ['STREAMER_ID'], token=os.environ['TWITCH_TOKEN'])

def prepare(bot:commands.Bot):
   bot.add_cog(StreamEvents(bot))