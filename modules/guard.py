import modules.banlist
import modules.bottiHelper
import modules.data.ids as ids

devIDs = [ ids.userIDs.ITZFLUBBY, ids.userIDs.WUB ]

allowedIDs = [ ids.userIDs.ITZFLUBBY, ids.userIDs.WUB ]

trustetIDs = [ ids.userIDs.CHRISTOPH, ids.userIDs.TITRA, ids.userIDs.LEO ]

allowed_roles = [ "Admin", "Dev", "Fachschaft ETEC", "Tutoren" ]

async def _checkBanlist(message, botData):
    for i in range(0, len(botData.botBanList)):
        if message.author.id == botData.botBanList[i][0]:
            if botData.botBanList[i][1] < 10:
                await modules.bottiHelper._sendMessagePingAuthor(message, ":customs: Du wurdest von der Nutzung des Bots ausgeschlossen _(BL: {})_!".format(str(botData.botBanList[i][1])))
                botData.botBanList[i][1] = botData.botBanList[i][1] + 1
            return False    
    return True

async def _checkPerms(botti, message, allowed, enableTrustet = False):
    if enableTrustet:
        if message.author.id in trustetIDs:
            return True
    if message.author.id in allowedIDs or any(role.name in allowed for role in message.author.roles):
        return True
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, "[:shield:] `Guard`: **Fehlende Berechtigung!**")
        return False

def _checkPermsQuiet(botti, message, allowed):
    if message.author.id in allowedIDs or any(role.name in allowed for role in message.author.roles):
        return True
    else:
        return False

async def _floodDetection(message, botti, botData): 
    try:
        lastAuthorID = botData.lastCommands[0].author.id
        sameAuthor = True
        for entry in botData.lastCommands:
            if entry.author.id is not lastAuthorID:
                sameAuthor = False
                break
                
        if sameAuthor:
            diff = (botData.lastCommands[len(botData.lastCommands) - 1].created_at) - (botData.lastCommands[0].created_at)
            if (diff.seconds - 86400) > -15:
                banmessage = await modules.bottiHelper._sendMessage(message, "[:shield:] `Guard`: **Flood erkannt! Nutzer {userMention} wird gebannt...**".format(message.author.mention))
                await modules.banlist.botban(botti, banmessage, botData)
    except:
        pass         
        
        