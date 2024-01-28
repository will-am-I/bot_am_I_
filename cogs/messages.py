from twitchio.ext import routines, commands, eventsub
from mysql.connector import connect
from datetime import datetime, timedelta
import os, twitchio

class Messages(commands.Cog):
   
   chatters = []

   def __init__(self, bot:commands.Bot):
      self.bot = bot
      self.eventClient = eventsub.EventSubWSClient(self.bot)
      self.bot.loop.create_task(self.sub())
      self.timed_messages.start()

   @commands.Cog.event()
   async def event_message(self, message:twitchio.Message):
      if message.echo or message.author.id == os.environ['STREAMER_ID']:
         return
      await self.bot.handle_commands(message)
      
      print(message.content)
      if message.author.id not in self.chatters:
         self.chatters.append(message.author.id)
         await message.channel.send(f"Welcome to the stream, {message.author.name}!")

      db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
      cursor = db.cursor()

      try:
         cursor.execute("UPDATE timed_messages SET message_count = message_count + 1")
         db.commit()
      except Exception as e:
         db.rollback()
         await message.channel.send("Error occurred with timed messages.")
         print(str(e))

      db.close()
   
   async def event_eventsub_notification_stream_start(self, event:eventsub.StreamOnlineData):
      print("Stream started")
      self.timed_messages.start()

   async def event_eventsub_notification_stream_end(self, event:eventsub.StreamOfflineData):
      print("Stream Ended")

      db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
      cursor = db.cursor()

      try:
         cursor.execute("UPDATE timed_messages SET message_count = 0")
         db.commit()
      except Exception as e:
         db.rollback()
         await event.broadcaster.channel.send("Error occurred when reseting timed messages.")
         print(str(e))

      db.close()

      self.chatters.clear()
      self.timed_messages.stop()

   async def sub(self):
      await self.eventClient.subscribe_channel_stream_start(broadcaster=os.environ['STREAMER_ID'], token=os.environ['TWITCH_TOKEN'])
      await self.eventClient.subscribe_channel_stream_end(broadcaster=os.environ['STREAMER_ID'], token=os.environ['TWITCH_TOKEN'])
   

   @routines.routine(minutes=1)
   async def timed_messages(self):
      db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
      cursor = db.cursor()

      try:
         cursor.execute("SELECT messageid, message, message_count, min_messages, min_minutes, DATE_FORMAT(last_sent, '%Y%m%d %H%i%s') AS last_sent, active FROM timed_messages")
         results = cursor.fetchall()
         for message in results:
            if message[6] == 'Y' and (int(message[2]) <= int(message[3]) or datetime.now() >= datetime.strptime(message[5], '%Y%m%d %H%M%S') - timedelta(minutes=int(message[4]))):
               cursor.execute(f"UPDATE timed_messages SET message_count = 0, last_sent = NOW() WHERE messageid = {message[0]}")
               streams = await self.bot.fetch_streams([os.environ['STREAMER_ID']])
               if streams:
                  await streams[0].user.channel.send(message[1])
         db.commit()
      except Exception as e:
         print("exception")
         db.rollback()
         streams = await self.bot.fetch_streams([os.environ['STREAMER_ID']])
         if streams:
            await streams[0].user.channel.send("Error occurred with timed messages.")
         print(str(e))

      db.close()

def prepare(bot:commands.Bot):
   bot.add_cog(Messages(bot))