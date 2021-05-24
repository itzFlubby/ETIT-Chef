import asyncio
import datetime
import discord
import json
import modules.bottiHelper
import modules.data.ids as ids
import requests
import time

class FoodLine():
    def __init__(self, pName, pValue):
        self.name = pName
        self.value = pValue

class Weekday():
    def __init__(self, pName, pIndex):
        self.name = pName
        self.index = pIndex

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
            
    weekdayOptions = {
        "mo": Weekday("Montag", 0),
        "di": Weekday("Dienstag", 1),
        "mi": Weekday("Mittwoch", 2),
        "do": Weekday("Donnerstag", 3),
        "fr": Weekday("Freitag", 4),
        "sa": Weekday("Samstag", 5),
        "so": Weekday("Sonntag", 6)
    }

    currentWeekday = datetime.datetime.now().weekday()
    requestedWeekday = None
    requestedWeekdayIndex = None

    mensaOptions = {
        "adenauerring": {
            "name": "Am Adenauerring",
            "foodLines": [
                FoodLine("l1", "Linie 1"),
                FoodLine("l2", "Linie 2"),
                FoodLine("aktion", "[Kœri]werk 11-14 Uhr"),
                FoodLine("pizza", "[pizza]werk")
            ]
        },
        "erzberger": {
            "name": "Erzbergstraße",
            "foodLines": [
                FoodLine("wahl1", "Wahlessen 1"),
                FoodLine("wahl2", "Wahlessen 2"),
                FoodLine("wahl3", "Wahlessen 3")
            ]
        },
        "gottesaue": {
            "name": "Schloss Gottesaue",
            "foodLines": [
                FoodLine("wahl1", "Wahlessen 1"),
                FoodLine("wahl2", "Wahlessen 2"),
            ]
        },
        "tiefenbronner": {
            "name": "Tiefbronner Straße",
            "foodLines": [
                FoodLine("wahl1", "Wahlessen 1"),
                FoodLine("wahl2", "Wahlessen 2"),
                FoodLine("gut", "Gut & Günstig"),
                FoodLine("buffet", "Buffet"),
                FoodLine("curryqueen", "[Kœri]werk")
            ]
        },
        "x1moltkestrasse": {
            "name": "Caféteria Moltkestraße 30",
            "foodLines": [
                FoodLine("gut", "Gut & Günstig"),
            ]
        }
    }
    
    requestedMensa = "adenauerring" # default
    
    params = [str.lower() for str in message.content.split(" ")]
    
    for weekday in weekdayOptions.keys():
        if weekday in params:
            requestedWeekday = weekday
            requestedWeekdayIndex = weekdayOptions[weekday].index
            if requestedWeekdayIndex > weekdayOptions["fr"].index:
                await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "mensa"))      
                return
        
    for mensa in mensaOptions.keys():
        if mensa in params:
            requestedMensa = mensa
    

    if requestedWeekday == None:
        modifyDate = 1 if (datetime.datetime.now().hour >= 15) else 0
        for weekday in weekdayOptions.keys():
            if weekdayOptions[weekday].index == (currentWeekday + modifyDate):
                requestedWeekday = weekday
                requestedWeekdayIndex = (currentWeekday + modifyDate)
                requestedDifference = modifyDate
    else:
        if (requestedWeekdayIndex - currentWeekday) <= 0:
            requestedDifference = len(weekdayOptions.keys()) - currentWeekday + requestedWeekdayIndex
        else:
            requestedDifference = requestedWeekdayIndex - currentWeekday
        
    currentDate = int(time.time())
    lastDate = int(list(jsonData[requestedMensa].keys())[-1])
    
    if (currentDate + (7 * 86400)) > lastDate: # 7 * 86400 : number of seconds in one week
        await modules.bottiHelper._sendMessagePingAuthor(message, ":fork_knife_plate: Aktualisiere JSON...\n")
        await _updateJson(botData)
        with open(botData.modulesDirectory + "/data/mensa/mensaData.txt", "r") as outfile: # Reload JSON
            jsonData = json.loads(outfile.read())
    
    for timestamp in jsonData[requestedMensa].keys():
        if int(timestamp) > currentDate - 86400 + (86400 * requestedDifference): # 86400 number of seconds in one day
            data = discord.Embed(
                title = "Mensa " + mensaOptions[requestedMensa]["name"],
                color = 0xfad51b,
                description = "{}, den {}".format(weekdayOptions[requestedWeekday].name, datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y'))
            )
            
            data.set_author(name = "🍽️ Mensa-Speiseplan")
            data.set_thumbnail(url = botti.user.avatar_url)
            data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
            
            for foodLine in mensaOptions[requestedMensa]["foodLines"]:
                for foodLineData in jsonData[requestedMensa][timestamp][foodLine.name]:
                    if ("nodata" in foodLineData) and foodLineData["nodata"]:
                        mealValues = "__Leider gibt es für diesen Tag hier keine Informationen!__"
                        break
                        
                    if "closing_start" in foodLineData:
                        mealValues = "__Leider ist hier heute geschlossen. Grund: {reason}__".format(reason = foodLineData["closing_text"])
                        break
                        
                    price = " ({price:.2f}€)".format(price = foodLineData["price_1"]) if not (foodLineData["price_1"] == 0) else ""
                    meal = "__{meal} {price}__\n".format(meal = foodLineData["meal"], price = price)
                    
                    dish = foodLineData["dish"]
                    mealValues += "{meal}{dish}\n".format(meal = meal, dish = dish) if not (dish in [ "", "." ]) else meal
    
                    allAdditions = ", ".join(addition for addition in foodLineData["add"])
                    
                    mealValues += "_Zusatz: [{additions}]_".format(additions = allAdditions) if not (allAdditions == "") else "_Keine Zusätze_"
                        
                    foodContainsStringToEmoji = {
                        "bio": ":earth_africa:",
                        "fish": ":fish:", 
                        "pork": ":pig2:", 
                        "pork_aw": ":pig:", 
                        "cow": ":cow2:",
                        "cow_aw": ":cow:",
                        "vegan": ":broccoli:",
                        "veg": ":salad:",
                        "mensa_vit": "Mensa Vital" 
                    }
                    
                    for foodContainsKey in foodContainsStringToEmoji.keys():
                        if foodLineData[foodContainsKey]:
                            mealValues += " " + foodContainsStringToEmoji[foodContainsKey]
                 
                    mealValues += "\n\n"
                data.add_field(name = "⠀\n:arrow_forward: {} :arrow_backward:".format(foodLine.value), value = mealValues + "\n", inline = False)
            break

    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
    
async def updatemensa(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl aktualisiert den Mensa-Speiseplan.
    !updatemensa
    """
    await _updateJson(botData)
    await modules.bottiHelper._sendMessagePingAuthor(message, ":fork_knife_plate: Der Mensa-Speiseplan wurde aktualisiert.")
    