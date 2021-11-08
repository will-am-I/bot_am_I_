import urllib.request, json, mysql.connector

with open('./config.json') as data:
   config = json.load(data)

def category (bot, user, categoryid=None, subcategoryid1=None, subcategoryid2=None, subcategoryid3=None, subcategoryid4=None, *args):
   if user['id'] == config['streamer']:
      db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
      cursor = db.cursor()
      try:
         cursor.execute("DELETE FROM twitch_category")
         db.commit()

         if categoryid is not None:
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

            cursor.execute(f'INSERT INTO twitch_category (gamename, gameid, categoryname, categoryid, subcategoryname1, subcategoryid1, subcategoryname2, subcategoryid2, subcategoryname3, subcategoryid3, subcategoryname4, subcategoryid4) VALUES ("{gamename}", "{gameid}", "{categoryname}", "{categoryid}", "{subcategoryname1}", "{subcategoryid1}", "{subcategoryname2}", "{subcategoryid2}", "{subcategoryname3}", "{subcategoryid3}", "{subcategoryname4}", "{subcategoryid4}")')
            db.commit()
            bot.send_message(confirmation)
         else:
            bot.send_message("Category set to NONE")
      except Exception as e:
         db.rollback()
         bot.send_message(f"Error occurred setting the category.")
         print(str(e))

      db.close()

def wr (bot, user, *args):
   db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute("SELECT gamename FROM twitch_category")
      name = cursor.fetchone()[0]
      if (game := getGame()).upper() == name.upper():
         cursor.execute("SELECT gameid, categoryname, categoryid, subcategoryname1, subcategoryid1, subcategoryname2, subcategoryid2, subcategoryname3, subcategoryid3, subcategoryname4, subcategoryid4 FROM twitch_category")
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

         bot.send_message(f"The current WR in {game} - {category} is {parseTime(wrtime)} by {player}")
      elif game == "Offline":
         bot.send_message("Will is currently offline and not running anything.")
      else:
         bot.send_message("Will is not currently running this game.")
   except Exception as e:
      bot.send_message("Error occured finding the world record.")
      print(str(e))

   db.close()

def pb (bot, user, *args):
   db = mysql.connector.connect(host="localhost", username=config['database_user'], password=config['database_pass'], database=config['database_schema'])
   cursor = db.cursor()

   try:
      cursor.execute("SELECT gamename FROM twitch_category")
      name = cursor.fetchone()[0]
      if (game := getGame()).upper() == name.upper():
         cursor.execute("SELECT categoryname, categoryid, subcategoryname1, subcategoryid1, subcategoryname2, subcategoryid2, subcategoryname3, subcategoryid3, subcategoryname4, subcategoryid4 FROM twitch_category")
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
            bot.send_message(f"Will's current PB in {game} - {category} is {parseTime(pbtime)}")
         else:
            bot.send_message(f"Will currently does not have a time on the leaderboard for {game} - {category}")
      elif game == "Offline":
         bot.send_message("Will is currently offline and not running anything.")
      else:
         bot.send_message("Will is not currently running this game.")
   except Exception as e:
      bot.send_message("Error occurred when finding Will's personal best.")
      print(str(e))

   db.close()

def race (bot, user, *args):
   bot.send_message("Go to https://kadgar.net/live/will_am_i_/R4NG3__ to view the race live with both streams!")

def getGame():
   url = 'https://api.twitch.tv/helix/streams?user_login=will_am_i_'
   header = {'Client-ID': config['client_id'], 'Authorization': 'Bearer ' + config['twitch_token']}
   request = urllib.request.Request(url, headers=header)
   with urllib.request.urlopen(request) as streamurl:
      streaminfo = json.loads(streamurl.read().decode())
      
   if (streaminfo['data']):
      gameid = streaminfo['data'][0]['game_id']
      request = urllib.request.Request('https://api.twitch.tv/helix/games?id=' + gameid, headers=header)
      with urllib.request.urlopen(request) as gameurl:
         game = json.loads(gameurl.read().decode())['data'][0]['name']
      print(game)
   else:
      game = "Offline"

   return game

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