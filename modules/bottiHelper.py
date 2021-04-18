import datetime
import discord
import linecache
import modules.data.ids as ids
import os

class BotError(Exception):
    pass

async def _checkCommandIgnoreList(message):
    commandIgnoreList = [ "pepo", "getfrogbot", "pepohelp", "aboutpepo", "froghelp" ]    
    if message.content.split(" ")[0][1:] in commandIgnoreList:
        await _sendMessage(message, "{emoji} Pepo-Befehl mit Präfix `!` erkannt. Ignoriere...".format(emoji = _constructEmojiString(ids.emojiIDs.PEPERETARDED)))
        return False   
        
async def _checkPingTrigger(botti, botData, message):
    if (not message.mention_everyone) and botti.user.mentioned_in(message) and (message.author.id not in [ ids.userIDs.ITZFLUBBY, ids.userIDs.CHRISTOPH ]):
        helpString = ":100: Ich wurde erwähnt und da bin ich. Mit `{prefix}help` zeige ich dir eine Hilfe an!".format(prefix = botData.botPrefix)
        try:
            await message.reply(helpString)
        except:
            await _sendMessagePingAuthor(message, helpString)
        
async def _checkPurgemaxConfirm(message, botData):
    if (botData.purgemaxConfirm) and (message.content != "{prefix}purgemax".format(prefix = botData.botPrefix)):
        await _sendMessagePingAuthor(message, ":exclamation: Purgemax abgebrochen.")
        botData.purgemaxConfirm = False
        
def _createDummyMessage(author, channel, content):
    msg = discord.Message(state = 0, channel = channel, data = { "id": 0, "webhook_id": 0, "attachments": [], "embeds": {}, "application": 0, "activity": 0, "edited_timestamp": 0, "type": 0, "pinned": 0, "mention_everyone": 0, "tts": 0, "content": content, "nonce": 0 })
    msg.author = author
    return msg  
 
def _constructEmojiString(emoji):
    return "<{emojiNoBracket}>".format(emojiNoBracket = _constructEmojiStringNoBracket(emoji))

def _constructEmojiStringNoBracket(emoji):
    return "{isAnimated}:{emojiName}:{emojiID}".format(isAnimated = ("a" if emoji["animated"] else ""), emojiName = emoji["name"], emojiID = emoji["id"])
 
async def _errorMessage(botti, message, botData, error):
    await _sendMessage(message, "```css\n[FAIL]: {0}```:fly: Bug automatisch an <@!{1}> gemeldet!".format(error, ids.userIDs.ITZFLUBBY))
    raise BotError("")

def _formatCommandLog(message):
    gotCMD = "=== BEFEHL ERHALTEN ===\nCMD: {}\nUSR: {}#{} ({})\nTME: {}\n".format(message.content, message.author.name, str(message.author.discriminator), str(message.author.id), message.created_at.strftime("UTC %Y-%m-%dT+%H:%M:%S"))
    if type(message.channel) is not discord.DMChannel:
        gotCMD = gotCMD + "CNL: {} ( {} )\n".format(message.channel.name, str(message.channel.id))
    else:
        gotCMD = gotCMD + "CNL: {} ( DM )\n".format(str(message.channel.id))

    return gotCMD
     
def _formatSlashCommandLog(ctx):
    time = "UNKNOWN"
    if ctx.message is not None:
        time = _toUTCTimestamp(ctx.message.created_at)
    return "=== BEFEHL ERHALTEN ===\nSLC: {}\nUSR: {}#{} ({})\nTME: {}\nCNL: {} ( {} )\n".format(ctx.name, ctx.author.name, str(ctx.author.discriminator), str(ctx.author.id), time, ctx.channel.name, str(ctx.channel.id))
    
def _getParametersFromMessage(content, maxLength):
    positions = [i for i in range(maxLength) if content.startswith("-", i)] 
    parameters = []
    for i in range(len(positions)):
        parameters.append(content[positions[i] + 1])
    return parameters

def _getTimestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT+%H:%M:%S")

def _toSTRFTimestamp(datetimeObject):
    return datetimeObject.strftime("%Y-%m-%dT+%H:%M:%S")

def _toUTCTimestamp(datetimeObject):
    return "UTC " + _toSTRFTimestamp(datetimeObject)

def _toGermanTimestamp(datetimeObject):
    return datetimeObject.strftime("%d.%m.%Y um %H:%M:%S")

def _invalidParams(botData, subcommand):
    return ":x: Ungültige Parameter! Verwende `{prefix}command {prefix}{subcommand}` für weitere Hilfe!".format(prefix = botData.botPrefix, subcommand = subcommand)

def _loadSettings(botData):
    with open(botData.configFile, "r") as conf:
        lines = conf.readlines()
     
    botData.botNormalStatus = lines[2][18:].replace("\n", "")
     
    if "= TRUE" in lines[3]:
        botData.maintenanceMode = True
    
    botData.baseDirectory = lines[4][17:]
    
def _logCommand(message, botData):
    botData.lastCommands =  botData.lastCommands[-1:] + botData.lastCommands[:-1]
    botData.lastCommands[0] = message
    
    if type(message.channel) is discord.DMChannel:
        return -1
    else:
        return 0

def _logSlashCommand(ctx, botData):
    ctx.defer()

    botData.lastCommands =  botData.lastCommands[-1:] + botData.lastCommands[:-1]
    botData.lastCommands[0] = ctx
        
def _maintenanceChange(configFile):
    with open(configFile, "r") as conf:
        lines = conf.readlines()
    with open(configFile, "w") as conf:
        if lines[3] == "MAINTENANCE = TRUE\n":
            lines[3] = "MAINTENANCE = FALSE\n"
        else:
            lines[3] = "MAINTENANCE = TRUE\n"
        for line in lines:
            conf.write(line)
            
async def _sendEmbed(message, content, embed):
    await message.channel.trigger_typing()
    await message.channel.send(content, embed = embed) 

async def _sendEmbedPingAuthor(message, content, embed):
    await message.channel.trigger_typing()
    await message.channel.send(message.author.mention + " " + content, embed = embed) 
                
async def _sendMessage(message, content):
    await message.channel.trigger_typing()
    return await message.channel.send(content)

async def _sendMessagePingAuthor(message, content):
    return await _sendMessage(message, "{} {}".format(content, message.author.mention))
        
async def _setNormalStatus(botti, botData):
    await botti.change_presence(activity = discord.Activity(name = botData.botNormalStatus, type = discord.ActivityType.listening), status = discord.Status.online)
    
async def _sendTTS(message, content):
    await message.channel.trigger_typing()
    await message.channel.send(content, tts = True)
            
def _spaceIntToString(integerToSpace):
    return str("{:,}".format(integerToSpace)).replace(",", " ")
            
def _versionInfo():
    return discord.__version__
            