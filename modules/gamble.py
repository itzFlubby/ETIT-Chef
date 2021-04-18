import asyncio
import discord
import modules.bottiHelper
import modules.data.ids as ids
import xlrd
import xlwt

from random import randint
from random import shuffle
from xlutils.copy import copy

async def balance(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt einen Kontostand an.
    !balance {@USER}
    {@USER} leer, Nutzer-Erwähnung
    !balance\r!balance @ETIT-Chef
    """
    user = message.author
    
    if len(message.mentions) != 0:
        user = message.mentions[0]

    balance = _getBalance(botData, user.id)
    if user.id == message.author.id:
        if balance == -1:
            _createAccount(botData, user.id)
            await modules.bottiHelper._sendMessagePingAuthor(message, ":slot_machine: Da du noch kein Konto hast, wurde für dich eben eins angelegt. Dein Kontostand beträgt nun **5 000** :cookie:!")
            return
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":slot_machine: Dein Kontostand beträgt **{}** :cookie:!".format(modules.bottiHelper._spaceIntToString(balance)))
    else:
        if balance == -1:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Nutzer {} hat kein Konto!".format(user.mention))
            return
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":slot_machine: Der Kontostand von {} beträgt **{}** :cookie:!".format(user.mention, modules.bottiHelper._spaceIntToString(balance)))

async def betflip(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl wirft eine Münzte mit Einsatz.
    !betflip {EINSATZ}
    {EINSATZ} Ganze Zahl >= 0
    !betflip 1000
    """
    try:
        betValue = message.content.split(" ")[1]
        if betValue.isdigit() != True and betValue != "allin":
            raise IndexError()
            
            
        if betValue == "allin":    
            betValue = _getBalance(botData, message.author.id)
        else:
            betValue = int(betValue)       
            
        checkBal = _checkBalance(botData, message.author.id, betValue)
        if checkBal == -1:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
            return   
        elif checkBal == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dafür reicht dein Kontostand nicht aus!")
            return 
            
        if randint(1, 100)  > 50:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":coin: Die Münze ist auf **Kopf** gelandet! Du hast **{}** :cookie: verloren!".format(modules.bottiHelper._spaceIntToString(betValue)))
            _addBalance(botData, message.author.id, -betValue)
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":coin: Die Münze ist auf **Zahl** gelandet! Du hast **{}** :cookie: gewonnen!".format(modules.bottiHelper._spaceIntToString(betValue)))
            _addBalance(botData, message.author.id, betValue)
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "betflip"))      
        return        

def _checkBalance(botData, userID, value):
    balance = _getBalance(botData, userID)
    if balance  == -1:
        return -1
    elif balance < value:
        return 0
    else:
        return 1

def _createAccount(botData, id):
    botData.balanceKeeper.append([id, 5000])

async def _cyclicBotDetection(botti, botData, runInLoop):
    channel = botti.get_guild(ids.guildIDs.ETIT_KIT).get_channel(ids.channelIDs.SPIELHALLE)
    run = True
    
    while(run):
        detectionStartMessage = channel.last_message
         
        await asyncio.sleep(20)
        
        allUsers = []
        async for message in channel.history(after = detectionStartMessage):
            if len(message.mentions) == 0:
                continue
            if message.mentions[0].id not in allUsers:
                allUsers.append(message.author.id)
                continue
            if message.author.id == botti.user.id:
                if len(message.mentions) == 1:
                    if message.mentions[0].id not in allUsers:
                        allUsers.append(message.mentions[0].id)
        
        if len(allUsers) == 0:
            await channel.send("```yaml\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=```\n:customs: Keine Nutzer erkannt. Zyklische Bot-Erkennung abgebrochen.\n⠀```yaml\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=```\n")
            return 
        
        await channel.edit(slowmode_delay = 25) 
        partialMessage = "```yaml\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=```\n:customs: Zyklische Bot-Erkennung aktiv.\nDrücke **innerhalb von 25s** auf die **bereits bestehende __geometrische__ Reaktion dieser Nachricht** __(farbiges Symbol, nicht die Flaggen)__.\nZ.B. 🟥 🟣 🔺 🔶```yaml\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=```"
        
        possiblePlaceholders = [ "!", "§", "$", "%", "&", "/", "(", ")", "=", "{", "[", "]", "}", "?" ]
        
        for i in range(0, 4):
            partialMessage = partialMessage + possiblePlaceholders[randint(0, len(possiblePlaceholders) - 1)] + "\n"    
        
        startMessage = await channel.send(partialMessage)
        
        possibleReactions = [ "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "⬛", "⬜", "🟫", "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "⚫", "⚪", "🟤", "🔺", "🔻", "🔸", "🔹", "🔶", "🔷" ]
        randomReaction = possibleReactions[randint(0, len(possibleReactions) - 1)]
        
        possibleFlags = [ "🇩🇪", "🇪🇺", "🇬🇧", "🇺🇳", "🇺🇸" ]
        randomFlag =  possibleFlags[randint(0, len(possibleFlags) - 1)]
        
        possibleEmojis = [ "😂", "☺", "😍", "🥳", "🤯", "😎", "🤩", "🧐" ]
        randomEmoji = possibleEmojis[randint(0, len(possibleEmojis) - 1)]
        
        reactionList = [ randomReaction, randomFlag, randomEmoji ]
        
        shuffle(reactionList)
        
        for reaction in reactionList:
            
            await startMessage.add_reaction(reaction)
        
        placeholderString = ""
        for i in range(randint(1, 4)):
            placeholderString = placeholderString + possiblePlaceholders[randint(0, len(possiblePlaceholders) - 1)] + "\n"
        
        await modules.bottiHelper._sendMessage(message, placeholderString)
        
        mentionString = ":customs: Erkannte Benutzer sind:\n"
       
        for i in range(len(allUsers)):
            mentionString = mentionString + "<@" + str(allUsers[i]) + ">\n"
            
        await channel.send(mentionString)
        
        
        
        await asyncio.sleep(26)
        
        startMessage = await channel.fetch_message(startMessage.id)

        for reaction in startMessage.reactions:
            try:
                if reaction.emoji == randomReaction:
                    async for reactedUser in reaction.users():
                        try:
                            allUsers.remove(reactedUser.id)
                        except:
                            pass
            except:
                pass
        
        endMessage = await channel.send("```yaml\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=```\n:customs: Zyklische Bot-Erkennung beendet.\n⠀```yaml\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=```\n")
        await channel.edit(slowmode_delay = 10)
        
        for userID in allUsers:
            await channel.send(":customs: <@{}> wurde vom Türsteher rausgeschmissen.".format(userID))
            overwrites = channel.overwrites             
            overwrites[message.guild.get_member(userID)] = discord.PermissionOverwrite( send_messages = False)
            await channel.edit(overwrites = overwrites)
            
        if runInLoop:
            await asyncio.sleep(60 * randint(20, 80))
        else:
            run = False

def _directSave(botti, botData):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Main sheet")

    for i in range(len(botData.balanceKeeper)):
        ws.write(i, 0, str(botData.balanceKeeper[i][0]))
        ws.write(i, 1, botData.balanceKeeper[i][1])

    wb.save(botData.modulesDirectory + "/data/balances/balances.xls")
    botData.balanceKeeper.clear()
    botData.balanceKeeper[:] = []
    _loadBalancesToKeeper(botti, botData)  

def _getBalance(botData, userID):
    balance = -1
    for i in range(len(botData.balanceKeeper)):
        if userID == botData.balanceKeeper[i][0]:
            balance = botData.balanceKeeper[i][1]
            break
    return int(balance)

async def guess(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl schätzt eine Zahl zwischen 1 und 100 mit Einsatz.
    !guess {ZAHL} {EINSATZ}
    {ZAHL} Ganze positive Zahl  <= 100
    {EINSATZ} Ganze Zahl >= 0
    !guess 50 1000
    """
    try:
        guessValue = message.content.split(" ")[1]
    
        betValue = message.content.split(" ")[2]
        if betValue.isdigit() != True and betValue != "allin" or guessValue.isdigit() != True:
            raise IndexError()
            
        guessValue = int(guessValue)
        if guessValue > 100:
            raise IndexError()
            
        if betValue == "allin":    
            betValue = _getBalance(botData, message.author.id)
        else:
            betValue = int(betValue)       
            
        checkBal = _checkBalance(botData, message.author.id, betValue)
        if checkBal == -1:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
            return   
        elif checkBal == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dafür reicht dein Kontostand nicht aus!")
            return    
            
        randomint = randint(0, 100)
        difference = abs(guessValue - randomint)

        if difference == 0:
            win = int(13 * betValue)
            winMessage = modules.bottiHelper._spaceIntToString(int(win)) + ":cookie:"
        elif difference < 2: 
            win = int(6 * betValue)
            winMessage = modules.bottiHelper._spaceIntToString(int(win)) + ":cookie:"           
        elif difference < 4: 
            win = int(4 * betValue)
            winMessage = modules.bottiHelper._spaceIntToString(int(win)) + ":cookie:"
        elif difference < 8: 
            win = int(2 * betValue)
            winMessage = modules.bottiHelper._spaceIntToString(int(win)) + ":cookie:"
        elif difference < 16: 
            win = int(1 * betValue)
            winMessage = modules.bottiHelper._spaceIntToString(int(win)) + ":cookie:"
        else:
            win = -betValue
            winMessage = "leider nichts"
        _addBalance(botData, message.author.id, win)   
        await modules.bottiHelper._sendMessagePingAuthor(message, ":game_die: Zufallszahl ist **{}**. Abstand von deinem Tipp ist **{}**! Damit hast du **{}** gewonnen!".format(randomint, difference, winMessage))    

    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "guess"))      
        return  

def _loadBalancesToKeeper(botti, botData):
    workbook = xlrd.open_workbook(botData.modulesDirectory + "/data/balances/balances.xls")
    sheet = workbook.sheet_by_index(0)
    ids = []
    botData.balanceKeeper.clear()
    botData.balanceKeeper[:] = []
    for i in range(sheet.nrows):
        if int(sheet.cell_value(rowx = i, colx = 0)) in ids:
            continue
        ids.append(int(sheet.cell_value(rowx = i, colx = 0)))
        botData.balanceKeeper.append([int(sheet.cell_value(rowx = i, colx = 0)), sheet.cell_value(rowx = i, colx = 1)])

async def norisknofun(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl geht ein großes Risiko ein. Sei gewarnt!
    !norisknofun {PARAM}
    {PARAM} String
    !norisknofun\r!norisknofun cancel
    """
    userBalance = _getBalance(botData, message.author.id)

    if _checkBalance(botData, message.author.id, userBalance) == -1:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
        return 
    if userBalance < 1000:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dafür ist dein Kontostand zu niedring. Mindestens **1 000** :cookie: benötigt!")
        return   
                
    if message.author.id not in botData.noRiskNoFunQueue:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":cookie: Bist du dir sicher, dass du `!norisknofun` ausführen willst?\n:cookie: Wenn du verlierst, dann verlierst du alles!\n:cookie: Zum Ausführen `!norisknofun` erneut eingeben, zum Abbrechen `!norisknofun cancel`!")
        botData.noRiskNoFunQueue.append(message.author.id)
    else:
        try:
            cancelMessage = message.content.split(" ")[1]
            await modules.bottiHelper._sendMessagePingAuthor(message, ":cookie: `!norisknofun` abgebrochen!")
            botData.noRiskNoFunQueue.remove(message.author.id)
        except:
            randomint = randint(0, 100)
              
            if randomint == 3:
                await modules.bottiHelper._sendMessagePingAuthor(message, ":cookie: <@&" + str(ids.roleIDs.SPIELHALLE) + "> UNGLAUBLICHER GEWINN!!! Damit hast du **{}** :cookie: gewonnen!".format(modules.bottiHelper._spaceIntToString(int(userBalance* 100))))
                _addBalance(botData, message.author.id, userBalance * 100) 
            else:
                await modules.bottiHelper._sendMessagePingAuthor(message, ":cookie: Damit hast du **{}** :cookie: verloren!".format(modules.bottiHelper._spaceIntToString(userBalance)))
                _addBalance(botData, message.author.id, -userBalance)  
            botData.noRiskNoFunQueue.remove(message.author.id)

async def rank(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt deine Position im Cookie-Ranking an.
    !rank {@USER}
    {@USER} leer, Nutzer-Erwähnung
    !rank\r!rank @ETIT-Chef
    """
    
    user = message.author
    if len(message.mentions) != 0:
        user = message.mentions[0]
        
    sortedList = sorted(botData.balanceKeeper, key = lambda x: int(x[1]), reverse = True)
    
    userRank = 0
    for i in range(len(sortedList)):
        userID = int(sortedList[i][0])
        if userID == user.id:
            userRank = i
            break
    
    paramString = "Du befindest"
    if user.id != message.author.id:
        paramString = "<@" + str(user.id) + "> befindet"
     
    await modules.bottiHelper._sendMessagePingAuthor(message, ":cookie: " + paramString + " sich im Ranking auf Platz **#" + str(userRank + 1) + "** (von " + str(len(sortedList)) + ") !")
    
async def ranking(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die fünf reichsten Nutzer an.
    !ranking
    """
    sortedList = sorted(botData.balanceKeeper, key = lambda x: int(x[1]), reverse = True)

    data = discord.Embed(
        title = "",
        color = 0xd300ff,
        description = ""
    )
    
    for i in range(5):
        user = message.guild.get_member(int(sortedList[i][0]))
        if user.nick is not None:
            nick = "({})".format(user.nick)
        else:
            nick = ""
            
        if i == 0:
            prefix = ""
            suffix = ":crown:"
        else:
            prefix = "⠀\n"
            suffix = "#" + str(i+1)
            
        data.add_field(name = "{}{} __{}#{}__ {}".format(prefix, suffix, user.name, user.discriminator, nick), value = modules.bottiHelper._spaceIntToString(int(sortedList[i][1])) + " :cookie:", inline = False)
    
    data.set_author(name = "🍪 Cookie-Leaderboard")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
 
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def rob(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl raubt etwas für dich aus.
    !rob
    """
    checkBal = _checkBalance(botData, message.author.id, 0)
    if checkBal == -1:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
        return       
    
    canRob = [ "eine Bank", "einen Bankautomaten", "einen Kassierer", "eine Tanke", "eine Tankstelle", "ein Geschäft", "ein Supermarkt", "die Kanzlerin", "einen Geldtransport" ]
    robActivities = [ "überfallen", "ausgeraubt", "geplündert", "abgezogen", "beraubt", "bestohlen" ]
    whileRobbing = [ "ist er auf seiner eigenen Rotze ausgerutscht", "ist er einfach blöd", "ist er einfach ein Grasdaggl", "war das Geld für ihn zu schwer", "hat er das nicht so gut geplant", "lief nicht alles nach Plan", "hatte er keinen Plan", "hat er sich das anders vorgestellt", "wusste er nicht mehr, was genau er machen soll", "hat er vergessen, was er da wollte" ]
    
    policeCame = [ "verhaftet", "verknackt", "geschnappt", "eingefangen", "verfolgt" ]
    
    if randint(1, 3) == 1:
        loss = float(randint(50, 100) / 100)
        _addBalance(botData, message.author.id, -int((_getBalance(botData, message.author.id) * loss)))
        await modules.bottiHelper._sendMessage(message, ":oncoming_police_car: {} hat **{}** {}. Jedoch wurde er **von der Polizei {}** und hat deshalb **{}%** seiner :cookie: verloren!".format(message.author.mention, canRob[randint(0, len(canRob) - 1)], robActivities[randint(0, len(robActivities) - 1)], policeCame[randint(0, len(policeCame) - 1)], int(loss * 100)))
        return 
    
    win = int(((randint(0, 2000) + randint(0, 2000)) / 2))
    _addBalance(botData, message.author.id, win)
    await modules.bottiHelper._sendMessage(message, ":money_mouth: {} hat **{}** {}. Jedoch **{}** und hat deshalb nur **{}** :cookie: erbeutet!".format(message.author.mention, canRob[randint(0, len(canRob) - 1)], robActivities[randint(0, len(robActivities) - 1)], whileRobbing[randint(0, len(whileRobbing) - 1)], modules.bottiHelper._spaceIntToString(win)))

def _addBalance(botData, userID, value):
    for i in range(len(botData.balanceKeeper)):
        if userID == botData.balanceKeeper[i][0]:
            botData.balanceKeeper[i][1] = botData.balanceKeeper[i][1] + value
            return 0
    return 1

async def _saveKeeperToFile(botti, botData):
    while True:
        await asyncio.sleep(3600 * 3)
        _directSave(botti, botData)
        botData.noRiskNoFunQueue.clear()

async def slots(botti, message, botData):    
    """ 
    Für alle ausführbar
    Dieser Befehl spielt Slots mit Einsatz.
    !slots {EINSATZ}
    {EINSATZ} Ganze Zahl >= 0
    !slots 1000
    """
    try:
        betValue = message.content.split(" ")[1]
        if betValue.isdigit() != True and betValue != "allin":
            raise IndexError()
            
            
        if betValue == "allin":    
            betValue = _getBalance(botData, message.author.id)
        else:
            betValue = int(betValue)      
            
        checkBal = _checkBalance(botData, message.author.id, betValue)
        if checkBal == -1:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
            return   
        elif checkBal == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dafür reicht dein Kontostand nicht aus!")
            return 
        
        slots = [ ":x:", ":zero:", ":apple:", ":watermelon:", ":palm_tree:", ":small_blue_diamond:", ":rocket:", ":100:" ] 
        randoms = [ randint(0, len(slots) - 1), randint(0, len(slots) - 1), randint(0, len(slots) - 1) ]

        result = "`================`\n:arrow_forward: {} {} {} :arrow_backward:\n`================`\n".format(slots[randoms[0]], slots[randoms[1]], slots[randoms[2]])
        
        if randoms[0] == 0 or randoms[1] == 0 or randoms[2] == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, "{}:slot_machine: Leider hast du nichts gewonnen!".format(result))
            _addBalance(botData, message.author.id, -betValue)
            return
        
        for i in range(len(randoms)):
            count = 0
            index = randoms[i]
            for j in range(i, len(randoms)):
                if randoms[j] == index:
                    count = count + 1
            if count > 1:
                break     
                
        if count == 1:
            await modules.bottiHelper._sendMessagePingAuthor(message, "{}:slot_machine: Leider hast du nichts gewonnen!".format(result))
            _addBalance(botData, message.author.id, -betValue)
            return
        elif count == 2:
            win = int(index * 0.7 * betValue)
            await modules.bottiHelper._sendMessagePingAuthor(message, "{}:slot_machine: Kleiner Gewinn! Du hast **{}** :cookie: gewonnen!".format(result, modules.bottiHelper._spaceIntToString(win)))    
            _addBalance(botData, message.author.id, win)
            return
        else:    
            win = int(index * 1.2 * betValue)
            await modules.bottiHelper._sendMessagePingAuthor(message, "{}:slot_machine: Großer Gewinn! Du hast **{}** :cookie: gewonnen!".format(result, modules.bottiHelper._spaceIntToString(win)))    
            _addBalance(botData, message.author.id, win)
            return           

    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "slots"))      
        return    

async def transfer(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl transferiert Geld.
    !transfer {@USER} {BETRAG}
    {@USER} Nutzer-Erwähnung
    {BETRAG} Ganze Zahl >= 0\r[Bei BETRAG > Kontostand werden alle Cookies überwiesen]
    !transfer @ETIT-Chef 1000
    """
    try:
        userToTransferTo = message.mentions[0]
    
        if userToTransferTo.id == message.author.id:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du kannst dir nicht selbst Cookies überweisen!")
            return                
            
        if userToTransferTo.id == ids.userIDs.ITZFLUBBY:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Diesem Nutzer kannst du keine Cookies überweisen!")
            return             
    
        transferValue = message.content.split(" ")[2]
        if transferValue.isdigit() != True:
            raise IndexError()
            
        transferValue = int(transferValue)
            
        checkBal = _checkBalance(botData, message.author.id, transferValue)
        if checkBal == -1:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
            return   
        elif checkBal == 0:
            transferValue = _getBalance(botData, message.author.id)
         
        if _getBalance(botData, userToTransferTo.id) == -1:
            _createAccount(botData, userToTransferTo.id)
            
        _addBalance(botData, message.author.id, -transferValue)
        _addBalance(botData, userToTransferTo.id, transferValue)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":money_with_wings: Du hast erfolgreich **{}** :cookie: an {} transferiert!".format(transferValue, userToTransferTo.mention))
        
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "transfer"))      
        return  

async def wheel(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl dreht das Glücksrad mit Einsatz.
    !wheel
    """
    costToPlay = 1000
    winAmounts = [ 1000, 2000, 3000, 10000, 25000, 60000, 100000, 1000000 ]
    
    checkBal = _checkBalance(botData, message.author.id, 1000)
    if checkBal == -1:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Sieht so aus, als hättest du wohl noch kein Konto. Verwende `!balance`, um eins anzulegen!")
        return 
    elif checkBal == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dafür reicht dein Kontostand nicht aus! Eine Teilnahme kostet **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(costToPlay)))
        return 
        

    wheelOfFortune = "`=====================================`\n:x: :cookie: :bell: :fleur_de_lis: :banana: :x: :crown: :coin: :cd: :magic_wand: :x:\n`=====================================`\n"
    
    possibleWins = (":x: `- Kein Gewinn` (50.00%)\n"
    ":cd: `-     {}` :cookie: (17.00%)\n"
    ":banana: `-     {}` :cookie: (12.50%)\n"
    ":bell: `-     {}` :cookie: (9.30%)\n"
    ":coin: `-    {}` :cookie: (6.00%)\n"
    ":magic_wand: `-    {}` :cookie: (3.50%)\n"
    ":fleur_de_lis: `-    {}` :cookie: (1.57%)\n"
    ":cookie: `-   {}` :cookie: (0.10%)\n"
    ":crown: `- {}` :cookie: (0.03%)\n"
    ).format(*map(modules.bottiHelper._spaceIntToString, winAmounts))
    
    randomint = randint(1, 10000)
    
    winMessage = ""
    
    winSelect = ""
    
    if randomint in range(1, 4):
        winSelect = ":blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :arrow_up: :blue_square: :blue_square: :blue_square: :blue_square:\n"
        winMessage = "**UNFASSBARER GEWINN**!!! Glückwunsch :partying_face: :crown:! **{}** :cookie: :cookie: <@&{}>".format(modules.bottiHelper._spaceIntToString(winAmounts[7]), str(ids.channelIDs.SPIELHALLE)) 
        _addBalance(botData, message.author.id, winAmounts[7] - costToPlay)
    elif randomint in range(4, 14):
        winSelect = ":blue_square: :arrow_up: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square:\n"
        winMessage = "**RIESEN GEWINN**!!! Glückwunsch :partying_face:! **{}** :cookie: :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[6]))
        _addBalance(botData, message.author.id, winAmounts[6] - costToPlay)
    elif randomint in range(14, 171):
        winSelect = ":blue_square: :blue_square: :blue_square: :arrow_up: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square:\n"
        winMessage = "**GROßER GEWINN**!!! Glückwunsch :partying_face:! **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[5]))
        _addBalance(botData, message.author.id, winAmounts[5] - costToPlay)        
    elif randomint in range(171, 521):
        winSelect = ":blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :arrow_up: :blue_square:\n"
        winMessage = "**Großer Gewinn**!! Glückwunsch :partying_face:! **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[4]))
        _addBalance(botData, message.author.id, winAmounts[4] - costToPlay)        
    elif randomint in range(521, 1121):
        winSelect = ":blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :arrow_up: :blue_square: :blue_square: :blue_square:\n"
        winMessage = "Großer Gewinn! Glückwunsch! **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[3]))
        _addBalance(botData, message.author.id, winAmounts[3] - costToPlay)  
    elif randomint in range(1121, 2051):
        winSelect = ":blue_square: :blue_square: :arrow_up: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square:\n"
        winMessage = "Kleiner Gewinn! Glückwunsch!! **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[2]))
        _addBalance(botData, message.author.id, winAmounts[2] - costToPlay)  
    elif randomint in range(2051, 3301):
        winSelect = ":blue_square: :blue_square: :blue_square: :blue_square: :arrow_up: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square:\n"
        winMessage = "Kleiner Gewinn! Glückwunsch! **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[1]))
        _addBalance(botData, message.author.id, winAmounts[1] - costToPlay)
    elif randomint in range(3301, 5001):
        winSelect = ":blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :blue_square: :arrow_up: :blue_square: :blue_square:\n"
        winMessage = "Mini Gewinn! Glückwunsch! **{}** :cookie:".format(modules.bottiHelper._spaceIntToString(winAmounts[0]))
        _addBalance(botData, message.author.id, winAmounts[0] - costToPlay) 
    else:
        winSelect = ":arrow_up: :blue_square: :blue_square: :blue_square: :blue_square: :arrow_up: :blue_square: :blue_square: :blue_square: :blue_square: :arrow_up:\n"
        winMessage = "Leider hast du keinen Gewinn :cry:!"
        _addBalance(botData, message.author.id, -costToPlay)  
        
    await modules.bottiHelper._sendMessagePingAuthor(message, "{}{}{}{}".format(wheelOfFortune, winSelect, possibleWins, winMessage))
    