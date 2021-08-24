import datetime
import discord
import linecache
import modules.data.ids as ids
import os

from __main__ import botti

class BotError(Exception):
    pass

async def _checkCommandIgnoreList(message):
    commandIgnoreList = [ "pepo", "getfrogbot", "pepohelp", "aboutpepo", "froghelp" ]    
    if message.content.split(" ")[0][1:] in commandIgnoreList:
        await _sendMessage(message, "{emoji} Pepo-Befehl mit Präfix `!` erkannt. Ignoriere...".format(emoji = _constructEmojiString(ids.emojiIDs.PEPERETARDED)))
        return False   
    return True
        
async def _checkPingTrigger(botti, botData, message):
    if (not message.mention_everyone) and botti.user.mentioned_in(message) and (message.author.id not in [ ids.userIDs.ITZFLUBBY, ids.userIDs.CHRISTOPH, ids.userIDs.ETIT_CHEF , ids.userIDs.ETIT_DEV ]):
        helpString = ":100: Ich wurde erwähnt und da bin ich. Mit `{prefix}help` zeige ich dir eine Hilfe an!".format(prefix = botData.botPrefix)
        try:
            await message.reply(helpString)
        except:
            await _sendMessagePingAuthor(message, helpString)

async def _checkSufficientPrivileges(botti, message, user):
    roles = message.guild.roles
    botRole = message.guild.get_role(ids.roleIDs.ETIT_BOT)
    
    if (roles.index(user.top_role) >= roles.index(botRole)) and (user.id != botti.user.id):
        await _sendMessagePingAuthor(message, ":x: Leider fehlt mir dazu die Berechtigung.")
        return False
    return True
    
    
async def _checkPurgemaxConfirm(message, botData):
    if (botData.purgemaxConfirm) and (message.content != "{prefix}purgemax".format(prefix = botData.botPrefix)):
        await _sendMessagePingAuthor(message, ":exclamation: Purgemax abgebrochen.")
        botData.purgemaxConfirm = False

def _convert_byte_sizes(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size

async def _createDM(botti, userID):
    user = botti.get_user(userID)
    if user.dm_channel is None:
        await user.create_dm()
    return user.dm_channel
    
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
    
def _formatContextMenuLog(ctx):
    time = "UNKNOWN"
    if self.target_message is not None:
        time = _toUTCTimestamp(self.target_message.created_at)
    return "=== BEFEHL ERHALTEN ===\nCMU: {}\nUSR: {}#{} ({})\nTME: {}\nCNL: {} ( {} )\n".format(ctx.name, ctx.target_author, str(ctx.author.discriminator), str(ctx.author.id), time, ctx.target_message.channel.name, str(ctx.target_message.channel.id))
    
def _getParametersFromMessage(content, maxLength):
    positions = [i for i in range(maxLength) if content.startswith("-", i)] 
    parameters = []
    for i in range(len(positions)):
        parameters.append(content[positions[i] + 1])
    return parameters

def _getTimestamp():
    return datetime.datetime.now().strftime("%d.%m.%Y um %H:%M:%S")

def _toSTRFTimestamp(datetimeObject):
    return datetimeObject.strftime("%d.%m.%Y um %H:%M:%S")

def _toUTCTimestamp(datetimeObject):
    return _toSTRFTimestamp(datetimeObject) + " UTC"

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
    
def _logCommand(botData, message = None, ctx = None):
    entryElement = message if message != None else ctx
    
    botData.lastCommands =  botData.lastCommands[-1:] + botData.lastCommands[:-1]
    botData.lastCommands[0] = entryElement
    
    botData.log.append(entryElement)
    botData.befehlsCounter += 1
    if len(botData.log) > 10:
        with open(botData.modulesDirectory + "data/log/log.txt", "a+") as f:
            for entry in botData.log:
                if type(entry) is discord.Message:
                    f.write(_formatCommandLog(entry))
                elif type(entry) is SlashContext:
                    f.write(_formatSlashCommandLog(entry))
                else:
                    f.write(_formatContextMenuLog(entry))
        botData.log.clear()
                    
    if type(entryElement.channel) is discord.DMChannel:
        return -1
    else:
        return 0
        
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
            
async def _sendMessage(message, content = "", embed = None, file = None, view = None):
    await message.channel.trigger_typing()
    if(view != None):
        return await message.channel.send(content, embed = embed, file = file, view = view)
    else:
        return await message.channel.send(content, embed = embed, file = file)
        
async def _sendMessagePingAuthor(message, content = "", embed = None, file = None, view = None):
    return await _sendMessage(message = message, content = "{} {}".format(content, message.author.mention), embed = embed, file = file)
        
async def _setNormalStatus(botti, botData):
    await botti.change_presence(activity = discord.Activity(name = botData.botNormalStatus, type = discord.ActivityType.listening), status = discord.Status.online)
    
async def _sendTTS(message, content):
    await message.channel.trigger_typing()
    await message.channel.send(content, tts = True)
            
def _spaceIntToString(integerToSpace):
    return str("{:,}".format(integerToSpace)).replace(",", " ")
            
def _versionInfo():
    return discord.__version__
            