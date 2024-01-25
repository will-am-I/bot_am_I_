import urllib.request, json, os, twitchio, typing, validators
from mysql.connector import connect
from twitchio.ext import commands

class SRC(commands.Cog):

   def __init__(self, bot:commands.Bot):
      self.bot = bot

   @commands.command()
   async def category (self, ctx:commands.Context, categoryid=None, subcategoryid1=None, subcategoryid2=None, subcategoryid3=None, subcategoryid4=None):
      db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
      cursor = db.cursor()

      try:
         if ctx.author.id == os.environ['STREAMER_ID']:
            if categoryid.upper() == "CLEAR":
               cursor.execute("DELETE FROM current_run")
               db.commit()

               await ctx.send("Category has been cleared")
            elif categoryid is not None:
               cursor.execute("DELETE FROM current_run")
               db.commit()

               with urllib.request.urlopen(f'https://www.speedrun.com/api/v1/categories/{categoryid}') as categoryjson:
                  categoryinfo = json.loads(categoryjson.read().decode())['data']
               categoryname = categoryinfo['name']

               with urllib.request.urlopen(categoryinfo['links'][1]['uri']) as gamejson:
                  gameinfo = json.loads(gamejson.read().decode())['data']
               gamename = gameinfo['names']['twitch']
               gameid = gameinfo['id']

               confirmation = f"Category set to {gamename} - {categoryname}"

               subcategoryname1 = None
               subcategoryname2 = None
               subcategoryname3 = None
               subcategoryname4 = None
               if subcategoryid1 is not None:
                  confirmation += " ("
                  with urllib.request.urlopen(f'https://www.speedrun.com/api/v1/categories/{categoryid}/variables') as variablesjson:
                     variablesinfo = json.loads(variablesjson.read().decode())['data']
                  for variable in variablesinfo:
                     if subcategoryid1 in variable['values']['values']:
                        subcategoryname1 = variable['values']['values'][subcategoryid1]['label']
                        confirmation += f"{subcategoryname1}, "
                     if subcategoryid2 is not None and subcategoryid2 in variable['values']['values']:
                        subcategoryname2 = variable['values']['values'][subcategoryid2]['label']
                        confirmation += f"{subcategoryname2}, "
                     if subcategoryid3 is not None and subcategoryid3 in variable['values']['values']:
                        subcategoryname3 = variable['values']['values'][subcategoryid3]['label']
                        confirmation += f"{subcategoryname3}, "
                     if subcategoryid4 is not None and subcategoryid4 in variable['values']['values']:
                        subcategoryname4 = variable['values']['values'][subcategoryid4]['label']
                        confirmation += f"{subcategoryname4}, "
                  confirmation = f"{confirmation[:-2]})"

               cursor.execute(f'INSERT INTO current_run (gamename, gameid, categoryname, categoryid, subcategoryname1, subcategoryid1, subcategoryname2, subcategoryid2, subcategoryname3, subcategoryid3, subcategoryname4, subcategoryid4) VALUES ("{gamename}", "{gameid}", "{categoryname}", "{categoryid}", "{subcategoryname1}", "{subcategoryid1}", "{subcategoryname2}", "{subcategoryid2}", "{subcategoryname3}", "{subcategoryid3}", "{subcategoryname4}", "{subcategoryid4}")')
               db.commit()
               await ctx.send(confirmation)
            else:
               cursor.execute("SELECT gamename, categoryname, subcategoryname1, subcategoryname2, subcategoryname3, subcategoryname4 FROM current_run")
               result = cursor.fetchone()[0]
               await ctx.send(f"Will is currently running {getCategory(result)}")
         else:
            cursor.execute("SELECT gamename, categoryname, subcategoryname1, subcategoryname2, subcategoryname3, subcategoryname4 FROM current_run")
            result = cursor.fetchone()[0]
            await ctx.send(f"Will is currently running {getCategory(result)}")

      except Exception as e:
         db.rollback()
         await ctx.send(f"Error occurred setting the category.")
         print(str(e))

      db.close()

   @commands.command()
   async def wr (self, ctx:commands.Context):
      db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
      cursor = db.cursor()

      try:
         cursor.execute("SELECT gamename FROM current_run")
         name = cursor.fetchone()[0]
         stream = await self.bot.fetch_streams([os.environ['STREAMER_ID']])
         print(stream)

         if not stream:
            await ctx.send("Will is currently offline.")
         elif (game := stream[0].game_name).upper() == name.upper():
            cursor.execute("SELECT gameid, categoryname, categoryid, subcategoryname1, subcategoryid1, subcategoryname2, subcategoryid2, subcategoryname3, subcategoryid3, subcategoryname4, subcategoryid4 FROM current_run")
            runinfo = cursor.fetchone()

            with urllib.request.urlopen(f'https://www.speedrun.com/api/v1/leaderboards/{runinfo[0]}/category/{runinfo[2]}') as leaderboardjson:
               leaderboard = json.loads(leaderboardjson.read().decode())['data']
            
            if runinfo[4] != 'None':
               variablecount = 1
               if runinfo[6] != 'None':
                  variablecount += 1
               if runinfo[8] != 'None':
                  variablecount += 1
               if runinfo[10] != 'None':
                  variablecount += 1

               records = []
               for record in leaderboard['runs']:
                  matchcount = 0
                  for value in record['run']['values']:
                     variable = record['run']['values'][value]
                     if variable == runinfo[4] or variable == runinfo[6] or variable == runinfo[8] or variable == runinfo[10]:
                        matchcount += 1
                  if matchcount == variablecount:
                     records.append(record)
                     
               records.sort(key=sortTime)
               currentwr = records[0]
            else:
               variablecount = 0
               currentwr = leaderboard['runs'][0]

            wrtime = currentwr['run']['times']['primary_t']

            players = []
            for player in currentwr['run']['players']:
               if player['rel'] == "user":
                  with urllib.request.urlopen(player['uri']) as playerinfo:
                     players.append(json.loads(playerinfo.read().decode())['data']['names']['international'])
               else:
                  players.append(player['name'])
            player = ", ".join([player for player in players])
            
            category = runinfo[1]
            if variablecount > 0:
               category = category + " ("
               if runinfo[4] != 'None':
                  category = category + runinfo[3] + ", "
               elif runinfo[6] != 'None':
                  category = category + runinfo[5] + ", "
               elif runinfo[8] != 'None':
                  category = category + runinfo[7] + ", "
               elif runinfo[10] != 'None':
                  category = category + runinfo[9] + ", "
               category = category[:-2] + ")"

            await ctx.send(f"The current WR in {game} - {category} is {parseTime(wrtime)} by {player}")
         else:
            await ctx.send("Will is not currently running this game.")
      except Exception as e:
         await ctx.send("Error occured finding the world record.")
         print(str(e))

      db.close()

   @commands.command()
   async def pb (self, ctx:commands.Context):
      db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
      cursor = db.cursor()

      try:
         cursor.execute("SELECT gamename FROM current_run")
         name = cursor.fetchone()[0]
         stream = await self.bot.fetch_streams([os.environ['STREAMER_ID']])

         if not stream:
            await ctx.send("Will is currently offline.")
         elif (game := stream[0].game_name).upper() == name.upper():
            cursor.execute("SELECT categoryname, categoryid, subcategoryname1, subcategoryid1, subcategoryname2, subcategoryid2, subcategoryname3, subcategoryid3, subcategoryname4, subcategoryid4 FROM current_run")
            runinfo = cursor.fetchone()

            variables = []
            hasPB = False
            with urllib.request.urlopen('https://www.speedrun.com/api/v1/users/18q2o608/personal-bests') as pbjson:
               records = json.loads(pbjson.read().decode())['data']
            for record in records:
               if record['run']['category'] == runinfo[1]:
                  variables = []
                  matchcount = 0
                  
                  for value in record['run']['values']:
                     with urllib.request.urlopen(f'https://www.speedrun.com/api/v1/variables/{value}') as valuejson:
                        issubcategory = json.loads(valuejson.read().decode())['data']['is-subcategory']
                     if issubcategory == True:
                        variables.append(record['run']['values'][value])
                  for variable in variables:
                     if variable == runinfo[3] or variable == runinfo[5] or variable == runinfo[7] or variable == runinfo[9]:
                        matchcount += 1
                  if matchcount == len(variables):
                     pbtime = record['run']['times']['primary_t']
                     hasPB = True
            
            category = runinfo[0]
            if len(variables) > 0:
               category = category + " ("
               if runinfo[3] != 'None':
                  category = category + runinfo[2] + ", "
               elif runinfo[5] != 'None':
                  category = category + runinfo[4] + ", "
               elif runinfo[7] != 'None':
                  category = category + runinfo[6] + ", "
               elif runinfo[9] != 'None':
                  category = category + runinfo[8] + ", "
               category = category[:-2] + ")"
               
            if hasPB:
               await ctx.send(f"Will's current PB in {game} - {category} is {parseTime(pbtime)}")
            else:
               await ctx.send(f"Will currently does not have a time on the leaderboard for {game} - {category}")
         else:
            await ctx.send("Will is not currently running this game.")
      except Exception as e:
         await ctx.send("Error occurred when finding Will's personal best.")
         print(str(e))

      db.close()

   @commands.command()
   async def race (self, ctx:commands.Context, url:typing.Optional[twitchio.PartialChatter]):
      if ctx.author.id == os.environ['STREAMER_ID'] and url is not None and validators.url(url):
         db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
         cursor = db.cursor()
         try:
            cursor.execute(f"UPDATE current_run SET raceurl = {url}")
            db.commit()
            await ctx.send(f"Race url set to {url}. Good luck!")
         except Exception as e:
            await ctx.send("Error occurred when updating the race url.")
            print(str(e))
         db.close()
      else:
         db = connect(host="localhost", username=os.environ['DB_USER'], password=os.environ['DB_PASS'], database=os.environ['DB_SCHEMA'])
         cursor = db.cursor()
         try:
            cursor.execute(f"SELECT raceurl FROM current_run")
            name = cursor.fetchone()[0]
            await ctx.send(f"Go to {url} to view the race live with both streams!")
         except Exception as e:
            await ctx.send("Error occurred when getting the race url.")
            print(str(e))
         db.close()

def getCategory(data):
   category = f"{data['gamename']} - {data['categoryname']}"

   if data['subcategory1'] is not None:
      category += f" ({data['subcategory1']}"
      if data['subcategory2'] is not None:
         category += f", {data['subcategory2']}"
         if data['subcategory3'] is not None:
            category += f", {data['subcategory3']}"
            if data['subcategory4'] is not None:
               category += f", {data['subcategory4']}"
      category += ")"

   return category


def parseTime(time_to_parse):
   sec, ms = divmod(time_to_parse * 100, 100)
   min, sec = divmod(sec, 60)
   hr, min = divmod(min, 60)

   ms = int(ms)
   sec = int(sec)
   min = int(min)
   hr = int(hr)
   
   if hr == 0:
      if min == 0:
         time = f'{sec:02}.{ms:02}'
      else:
         time = f'{min}:{sec:02}'
         
         if ms > 0:
            time = time + f'.{ms:02}'
   else:
      time = f'{hr}:{min:02}:{sec:02}'
      
      if ms > 0:
         time = time + f'.{ms:02}'

   return time

def sortTime(record):
   return int(record['run']['times']['primary_t'])

def prepare(bot:commands.Bot):
   bot.add_cog(SRC(bot))