import discord
import modules.bottiHelper
import modules.data.ids as ids
import xlrd
import xlwt

from xlutils.copy import copy

async def botban(botti, message, botData):
    """
    Reserviert für Entwickler
    Dieser Befehl bannt einen Nutzer von der Nutzung des Bots.
    !botban {@USER}
    {@user} Nutzer-Erwähnung
    !botban @ETIT-Chef
    """
    try:
        user = message.mentions[0]
        
        if user.id == ids.userIDs.ITZFLUBBY:
            return
            
        botData.botBanList.append([user.id, 1])
        for entry in botData.botBanList:
            if entry[0] == user.id:
                await modules.bottiHelper._sendMessagePingAuthor(message, ":customs: Dieser Nutzer ist bereits von der Nutzung des Bots gebannt!")
                return
        await modules.bottiHelper._sendMessagePingAuthor(message, ":customs: Der Nutzer {} wurde von der Nutzung des Bots gebannt _(BL: 1)_!".format(user.mention))  
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!botban"))      
        return            

async def botunban(botti, message, botData):
    """
    Reserviert für Entwickler
    Dieser Befehl entbannt einen Nutzer von der Nutzung des Bots.
    !botban {@USER}
    {@user} Nutzer-Erwähnung
    !botban @ETIT-Chef
    """
    try:
        user = message.mentions[0]
        for i in range(0, len(botData.botBanList)):
            if user.id == botData.botBanList[i][0]:
                del botData.botBanList[i]
        await modules.bottiHelper._sendMessagePingAuthor(message, ":customs: {} darf den Bot wieder benutzen!".format(user.mention))    
    except ValueError:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Nutzer ist nicht von der Nutzung des Bots gebannt!")             
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!botunban"))     
 
def _directSave(botData):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Main sheet")

    for i in range(len(botData.botBanList)):
        ws.write(i, 0, str(botData.botBanList[i][0]))
        ws.write(i, 1, botData.botBanList[i][1])

    wb.save(botData.modulesDirectory + "/data/banlist/banlist.xls")
    botData.botBanList.clear()
    botData.botBanList[:] = []
    _loadBotBans(botData)   
 
async def listbotbans(botti, message, botData):
    """
    Reserviert für Entwickler
    Dieser Befehl listet alle Nutzer, die von der Nutzung des Bots gebannt sind.
    !listbotbans
    """
    if len(botData.botBanList) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":customs: Zurzeit ist niemand von der Nutzung des Bots gebannt!")
        return
     
    all_bans = "```\n"
    for entry in botData.botBanList:
        user = botti.get_user(entry[0])
        all_bans += user.name + "#" + user.discriminator + " (ID: " + str(user.id) + ") | BL: " + str(entry[1]) + "\n"
        
    await modules.bottiHelper._sendMessage(message, content = ":customs: Die folgenden Nutzer sind von der Nutzung des Bots gebannt {}: {}".format(message.author.mention, all_bans + "```"))         

def _loadBotBans(botData):
    workbook = xlrd.open_workbook(botData.modulesDirectory + "/data/banlist/banlist.xls")
    sheet = workbook.sheet_by_index(0)
    ids = []
    botData.botBanList.clear()
    botData.botBanList[:] = []
    for i in range(sheet.nrows):
        if int(sheet.cell_value(rowx = i, colx = 0)) in ids:
            continue
        ids.append(int(sheet.cell_value(rowx = i, colx = 0)))
        botData.botBanList.append([int(sheet.cell_value(rowx = i, colx = 0)), sheet.cell_value(rowx = i, colx = 1)])