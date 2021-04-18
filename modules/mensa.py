import asyncio
import datetime
import discord
import json
import modules.bottiHelper
import modules.data.ids as ids
import requests
import time

async def mensa(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl zeigt den Speiseplan an.
    !mensa {MENSA} {TAG}
    {MENSA} "", "adenauerring", "erzberger", "gottesaue", "tiefenbronner", "x1moltkestrasse"
    {TAG} "", "mo", "di", "mi", "do", "fr", "sa", "so"
    !mensa\!mensa mo\r!mensa adenauerring fr
    """
    with open(botData.modulesDirectory + "/data/mensa/mensaData.txt", "r") as outfile:
        jsonData = json.loads(outfile.read())
        
    currentDate = int(time.time())
    lastDate = int(list(jsonData["adenauerring"].keys())[-1])
    
    if (currentDate + (7 * 86400)) > lastDate:
        await modules.bottiHelper._sendMessage(message, ":fork_knife_plate: Aktualisiere JSON... Dies dauert ein paar Sekunden...\n")
        await _updateJson(botData)
        await asyncio.sleep(5)
    
    weekdayOptions = [ "mo", "di", "mi", "do", "fr", "sa", "so" ]
    weekdayNames = [ "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag" ]
    
    requestedWeekday = -1
    
    mensaOptions = [ "adenauerring", "erzberger", "gottesaue", "tiefenbronner", "x1moltkestrasse" ]
    mensaNames = [ "Am Adenauerring", "Erzbergstraße", "Schloss Gottesaue", "Tiefbronner Straße", "Caféteria Moltkestraße 30" ]
    
    requestedMensa = -1
    
    try:
        if message.content.split(" ")[1].lower() in weekdayOptions or message.content.split(" ")[1].lower() in mensaOptions:
            for i in range(len(weekdayOptions)): #Wochentag
                if message.content.split(" ")[1].lower() == weekdayOptions[i]:
                    requestedWeekday = i
            for i in range(len(mensaOptions)): #Mensa       
                if message.content.split(" ")[1].lower() == mensaOptions[i]:
                    requestedMensa = i
                    
            if requestedWeekday != -1:
                for i in range(len(mensaOptions)):      
                    if message.content.split(" ")[2].lower() == mensaOptions[i]:
                        requestedMensa = i   
            
            if requestedMensa != -1:
                for i in range(len(mensaOptions)):      
                    if message.content.split(" ")[2].lower() == weekdayOptions[i]:
                        requestedWeekday = i       
    except: 
        pass
    
    
    currentWeekday = datetime.datetime.now().weekday()
    
    if datetime.datetime.now().hour >= 15 and requestedWeekday == -1:
        requestedWeekday = currentWeekday + 1   

    if requestedWeekday > 4:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!mensa"))      
        return
    
    if requestedWeekday != - 1:
        if (requestedWeekday - currentWeekday) <= 0:
            requestedDifference = len(weekdayNames) - currentWeekday + requestedWeekday
        else:
            requestedDifference = requestedWeekday - currentWeekday
    else:
        requestedWeekday = currentWeekday
        requestedDifference = 0
        
    if requestedMensa == -1:    
        requestedMensa = 0
    
    foodLines = [ 
    [ "l1", "l2", "aktion", "pizza" ], 
    [ "wahl1", "wahl2", "wahl3" ], 
    [ "wahl1", "wahl2" ], 
    [ "wahl1", "wahl2", "gut", "buffet", "curryqueen" ], 
    [ "gut" ], 
    ]

    foodLineNames = [ 
    [ "Linie 1", "Linie 2", "[Kœri]werk 11-14 Uhr", "[pizza]werk" ],
    [ "Wahlessen 1", "Wahlessen 2", "Wahlessen 3" ], 
    [ "Wahlessen 1", "Wahlessen 2" ], 
    [ "Wahlessen 1", "Wahlessen 2", "Gut & Günstig", "Buffet", "[Kœri]werk" ], 
    [ "Gut & Günstig" ], 
    ]            
    
    for key in jsonData["adenauerring"].keys():
        if int(key) > currentDate - 86400 + (86400 * requestedDifference):
            data = discord.Embed(
                title = "Mensa " + mensaNames[requestedMensa],
                color = 0xfad51b,
                description = "{}, den {}".format(weekdayNames[requestedWeekday], datetime.datetime.fromtimestamp(int(key)).strftime('%d.%m.%Y'))
            )
            
            data.set_author(name = "🍽️ Mensa-Speiseplan")
            data.set_thumbnail(url = botti.user.avatar_url)
            data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
            
            counter = 0
            for foodLine in foodLines[requestedMensa]: 
                foodLineName = foodLineNames[requestedMensa][counter]
                mealValues = ""
                try:
                    for i in range(len(jsonData[mensaOptions[requestedMensa]][key][foodLine])):
                        try:
                            noData = jsonData[mensaOptions[requestedMensa]][key][foodLine][i]["nodata"]
                            if noData == True:
                                mealValues = "__Leider gibt es für diesen Tag hier keine Informationen!__"
                                break
                        except:
                            pass
                    
                        meal = jsonData[mensaOptions[requestedMensa]][key][foodLine][i]["meal"]
                        price = " (" + format(jsonData[mensaOptions[requestedMensa]][key][foodLine][i]["price_1"], ".2f") + "€)"
                        if price == " (0.00€)":
                            price = ""
                        meal = "__" + meal + price + "__\n"
                        
                        dish = jsonData[mensaOptions[requestedMensa]][key][foodLine][i]["dish"]
                        if dish != "" and dish != ".":
                            mealValues = mealValues + meal + dish + "\n"
                        else:
                            mealValues = mealValues + meal

                        additions = len(jsonData[mensaOptions[requestedMensa]][key][foodLine][i]["add"])
                        if additions > 1:
                            additionString = "["
                            for j in range(additions):
                                additionString = additionString + jsonData[mensaOptions[requestedMensa]][key][foodLine][i]["add"][j] + ", "
                                
                            additionString = additionString[:-2] + "]"
                            
                            mealValues = mealValues + "_Zusatz: " + additionString + "_"
                        else:
                            mealValues = mealValues + "_Keine Zusätze_ "
                            
                        foodContainsStrings = [ "bio", "fish", "pork", "pork_aw", "cow", "cow_aw", "vegan", "veg", "mensa_vit" ]
                        foodContainsEmojis = [ ":earth_africa:", ":fish:", ":pig2:", ":pig:", ":cow2:", ":cow:", ":broccoli:", ":salad:", "Mensa Vital" ]
                        
                        for j in range(len(foodContainsStrings)):
                            if jsonData[mensaOptions[requestedMensa]][key][foodLine][i][foodContainsStrings[j]] == True:
                                mealValues = mealValues + " " + foodContainsEmojis[j]
                                
                        mealValues = mealValues + "\n\n"    
                    counter = counter + 1
                    
                    data.add_field(name = "⠀\n:arrow_forward: " + foodLineName + " :arrow_backward:", value = mealValues + "\n", inline = False)
                except KeyError:
                    counter = counter + 1
            break

    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def mensazusatz(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl listet alle Mensazusätze auf.
    !mensazusatz
    """
    mensaZusatzString = ("```yaml\n"
    "(1) mit Farbstoff\n"
    "(2) mit Konservierungsstoff\n"
    "(3) mit Antioxidationsmittel\n"
    "(4) mit Geschmacksverstärker\n"
    "(5) mit Phosphat\n"
    "(6) Oberfläche gewachst\n"
    "(7) geschwefelt\n"
    "(8) Oliven geschwärzt\n"
    "(9) mit Süßungsmittel\n"
    "(10) - kann bei übermäßigem Verzehr abführend wirken\n"
    "(11) - enthält eine Phenylalaninquelle\n"
    "(12) - kann Restalkohol enthalten\n"
    "(14) - aus Fleischstücken zusammengefügt\n"
    "(15) - mit kakaohaltiger Fettglasur\n"
    "(27) - aus Fischstücken zusammengefügt\n"
    "Mensa Vital - Mensa Vital\n"
    "LAB - mit tierischem Lab\n"
    "GEL - mit Gelatine```"
    ":cow2: `- enthält Rindfleisch`\n"
    ":cow: `- enthält regionales Rindfleisch aus artgerechter Tierhaltung`\n"
    ":pig2: `- enthält Schweinefleisch`\n"
    ":pig: `- enthält regionales Schweinefleisch aus artgerechter Tierhaltung`\n"
    ":salad: `- vegetarisches Gericht`\n"
    ":broccoli: `- veganes Gericht`\n"
    ":earth_africa: `- kontrolliert biologischer Anbau mit EU Bio-Siegel / DE-Öko-007 Kontrollstelle`\n"
    ":fish: `- MSC aus zertifizierter Fischerei`\n")
    await modules.bottiHelper._sendMessage(message, ":fork_knife_plate: Dies sind die Mensa-Zusätze {}:\n{}Eine komplette Liste aller gesetzlich ausweisungspflichtigen Zusatzstoffe und Allergene findest du unter:\n{}".format(message.author.mention, mensaZusatzString, botData.mensaZusatzURL))

async def _updateJson(botData):
    response = requests.get(url = botData.mensaURL, auth = requests.auth.HTTPBasicAuth(botData.mensaUsername, botData.mensaUserpassword))
    
    jsonResponse = response.content
    
    jsonData = json.loads(jsonResponse.decode('utf8'))
    
    with open(botData.modulesDirectory + "/data/mensa/mensaData.txt", 'w') as outfile:
        json.dump(jsonData, outfile)

async def _dailyMensa(botti, botData):
    while(True):
        now = datetime.datetime.now()
        nextPing = now
        if now.hour > 8:
            nextPing = now + datetime.timedelta(days = 1)

        nextPing = datetime.datetime(nextPing.year, nextPing.month, nextPing.day, 8, 0, 0)
        
        diff = nextPing - now
        
        await asyncio.sleep(diff.seconds)
        
        if nextPing.weekday() < 4:
            msg = modules.bottiHelper._createDummyMessage(botti.get_guild(ids.serverIDs.ETIT_KIT).get_member(botti.user.id), discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.MENSA), "")
            await modules.mensa.mensa(botti, msg, botData)