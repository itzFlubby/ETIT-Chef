import asyncio
import datetime
import discord
import json
import modules.banlist
import modules.bottiHelper
import modules.data.ids as ids
import modules.gamble
import os
import sys
import xlrd
import xlwt

from discord_slash import SlashContext

import requests

async def balancekeeper(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl zeigt alle registrierten Kontostände an.
    !balancekeeper
    """
    sortedList = sorted(botData.balanceKeeper, key = lambda x: int(x[1]), reverse = True)

    totalStrings = []
    wasTooLongForSingleMessage = False
    
    totalString = ":cookie: Alle registrierten Kontostände: \n```ml\nUSERNAME#DISCRIMINATOR |       USERID       |  BALANCE  \n"
    
    for entry in sortedList:
        
        user = message.guild.get_member(entry[0])
        
        if user == None: # Wenn Nutzer Server verlassen oder gelöscht wurde
            continue
            
        
        userNameAndDiscriminator = "{}#{}".format(user.name, str(user.discriminator))
        
        if len(userNameAndDiscriminator) > 22: # 22 = len("USERNAME#DISCRIMINATOR")
            userNameAndDiscriminator = userNameAndDiscriminator[:19] + "..." # 19 = len("USERNAME#DISCRIMINATOR") - len("...")
        
        totalString += "{:<23}| {:<18} | {}\n".format(userNameAndDiscriminator, entry[0],  modules.bottiHelper._spaceIntToString(int(entry[1])))
       
        if len(totalString) > botData.maxMessageLength:
            wasTooLongForSingleMessage = True
            totalStrings.append(totalString + "```")
            totalString = "```ml\n"
            
    if wasTooLongForSingleMessage:
        totalStrings.append(totalString + "```")
        
    for string in totalStrings:
        await modules.bottiHelper._sendMessage(message, string) 

async def botdetection(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl startet die Bot-Detection in der Spielhalle.
    !botdetection
    """
    await modules.gamble._cyclicBotDetection(botti, botData, False)

async def commandlist(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl zeigt eine vollständige, ungekürzte Befehls-Liste.
    !commandlist
    """
    data = discord.Embed(
        title = "_Vollständige Befehls-Liste_",
        color = 0x800080,
        description = ""
    )
    
    for commandModule in botData.allCommandModules:
        data.add_field(name = commandModule.moduleName.capitalize(), value = commandModule.commandNameList, inline = False)
        
    data.add_field(name = "Slash-Commands", value = botData.slashCommandList, inline = False)
    
    data.set_thumbnail(url = botti.user.avatar.url)
    data.set_author(name = botti.user.name + "#" + str(botti.user.discriminator), icon_url = "https://cdn.discordapp.com/app-assets/" + str(botti.user.id) + "/" + str(ids.assetIDs.PROFILE_PICTURE) + ".png")
    data.set_footer(text = "Insgesamt sind das " + str(botData.totalCommands) + " Befehle!")
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

async def devtest(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl ist zur reinen Entwicklung und macht jedes mal etwas anderes.
    !devtest {*ARGS}
    {*ARGS} *args
    !devtest
    """ 
    pass
    
async def give(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl manipuliert Kontostände.
    !give {@USER} {BETRAG}
    {@USER} Nutzer-Erwähnung
    {BETRAG} Ganze Zahl
    !give @ETIT-Chef 500\r!give @ETIT-Chef -500
    """
    try:
        user = message.mentions[0]
        value = message.content.split(" ")[2]
        
        
        if value[0] == "-":
            if not value[1:].isdigit():
                raise IndexError()
            else:
                value = -1 * int(value[1:])
        else:
            if not value.isdigit():
                raise IndexError()
            else:
                value = int(value)
        
        userCookies = modules.gamble._getBalance(botData, user.id)
        if (userCookies + value) < 0:
            value = -userCookies
        
        returnVal = modules.gamble._addBalance(botData, user.id, value)
        if returnVal == 1:
            await modules.bottiHelper._sendMessagePingAuthor(message, "{emoji} {currencyNamePlural} konnten an {userMention} __nicht__ vergeben werden!".format(emoji = botData.botCurrency["emoji"], currencyNamePlural = botData.botCurrency["plural"], userMention = user.mention)) 
            return
        await modules.bottiHelper._sendMessagePingAuthor(message, "{emoji} **{value}** {currencyNamePlural} an {userMention} vergeben!".format(emoji = botData.botCurrency["emoji"], value = modules.bottiHelper._spaceIntToString(value), currencyNamePlural = botData.botCurrency["plural"], userMention = user.mention)) 
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "give"))      
        return   

async def lastcommands(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl zeigt die letzten fünf ausgeführten Befehle an.
    !lastcommands
    """
    lastCommandsStr = ":screwdriver: Dies sind die zuletzt ausgeführten Befehle:\n```yaml\n"
    for cmd in botData.lastCommands:
        if cmd == None or isinstance(cmd, int):
            break

        if not isinstance(cmd, SlashContext):
            lastCommandsStr = lastCommandsStr + modules.bottiHelper._formatCommandLog(cmd)
        else:
            lastCommandsStr = lastCommandsStr + modules.bottiHelper._formatSlashCommandLog(cmd)
            
    await modules.bottiHelper._sendMessagePingAuthor(message, lastCommandsStr + "```")

async def maintenance(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl ändert den Maintenance-Mode.
    !maintenance
    """
    if botData.maintenanceMode:
        botData.maintenanceMode = False
        await modules.bottiHelper._sendMessage(message, ":tools: Die Wartungsarbeiten sind **abgeschlossen**!")
        await modules.bottiHelper._setNormalStatus(botti, botData)
        modules.bottiHelper._maintenanceChange(botData.configFile)
    else:
        botData.maintenanceMode = True
        await modules.bottiHelper._sendMessage(message, ":tools: Die Wartungsarbeiten haben **begonnen**!")
        await botti.change_presence(activity = discord.Game(name = "⚒ Wartungsarbeiten ⚒"), status = discord.Status.dnd)
        modules.bottiHelper._maintenanceChange(botData.configFile)

async def modulelist(botti, message, botData):
    """
    Reserviert für Entwickler
    Dieser Befehl zeigt alle Befehle eines Moduls an.
    !modulelist {MODUL}
    {MODUL} String [Modul-Name]
    !modulelist utils
    """
    try:
        wantedModule = message.content.split(" ")[1].lower()
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "modulelist"))
        return
        
    data = discord.Embed(
        title = "_Befehls-Liste von {}_".format(wantedModule.capitalize()),
        color = 0x800080,
        description = ""
    )    
    data.set_thumbnail(url = botti.user.avatar.url)
    data.set_author(name = botti.user.name + "#" + str(botti.user.discriminator), icon_url = "https://cdn.discordapp.com/app-assets/" + str(botti.user.id) + "/" + str(ids.assetIDs.PROFILE_PICTURE) + ".png")
    
    for commandModule in botData.allCommandModules:
        if wantedModule == commandModule.moduleName:
            data.add_field(name = commandModule.moduleName.capitalize(), value = commandModule.commandNameList)
            data.set_footer(text = "{} hat {} Befehle!".format(commandModule.moduleName.capitalize(), len(commandModule.commandNameList)))
            await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)
            return
    
    await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "modulelist"))

async def restart(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl startet den Bot neu.
    !restart {PARAMS}
    {PARAMS} -n [Neustart, ohne speichern]
    !restart\r!restart -n
    """
    params = modules.bottiHelper._getParametersFromMessage(message.content, 11) # 11 = len("!restart -q")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":infinity: **[RESTART]**  `@{}`".format(modules.bottiHelper._getTimestamp()))
    print("[ INFO ] Der Bot wurde von **{0}#{1}** neugestartet!".format(message.author.name, message.author.discriminator))
    print("---")
    if "n" not in params:
        await save(botti, message, botData)
    os.execv("/usr/local/bin/python3.8", ["python"] + [botData.baseDirectory + "ETIT-Chef.py"])

async def save(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl speichert die Variablen.
    !save
    """
    modules.gamble._directSave(botti, botData)
    modules.banlist._directSave(botData)
    await modules.bottiHelper._sendMessagePingAuthor(message, ":arrow_down: Variablen gespeichert!")

async def say(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl sagt etwas im Namen des Bots.
    !say {MESSAGE}
    {MESSAGE} String
    !say ICH BIN COOL!
    """
    channelToSend = message.channel
    try:
        if len(message.channel_mentions) != 0:
            channelToSend = message.channel_mentions[0]
            messageToSendPartial = str(message.content[5:]).split(" ")
            messageToSend = ""
            for i in range(1, len(messageToSendPartial)):
                messageToSend = messageToSend + messageToSendPartial[i] + " "
        else:    
            messageToSend = message.content[5:]
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "say"))      
        return
    await channelToSend.trigger_typing()
    await channelToSend.send(messageToSend)  

async def shutdown(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl fährt den Bot herunter.
    !shutdown
    """
    await modules.bottiHelper._sendMessagePingAuthor(message, ":arrow_heading_down: **[SHUTDOWN]** `@{}`".format(modules.bottiHelper._getTimestamp()))
    await save(botti, message, botData)
    await botti.logout()
    await botti.close()
    print("[ INFO ] Der Bot wurde von **{0}#{1}** heruntergefahren!".format(message.author.name, message.author.discriminator))
    print("---")
    raise SystemExit

async def throwexception(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl erzeugt eine Fehlermeldung.
    !throwexception
    """
    raise RuntimeError("throwexception(args) called. RuntimeError raised.") 

async def traceback(botti, message, botData):
    """ 
    Reserviert für Entwickler 
    Dieser Befehl zeigt den Traceback des letzten Errors an.
    !traceback
    """
    if botData.lastError == "":  
        await modules.bottiHelper._sendMessagePingAuthor(message, ":warning: Bisher ist noch kein Fehler aufgetreten!")
        return
    if len(botData.lastError) > botData.maxMessageLength:
        runs = 0
        for i in range(0, len(botData.lastError), botData.maxMessageLength):
            await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.BOT_TEST_LOBBY).send(content = "```py\n{}```".format(botData.lastError[(botData.maxMessageLength*runs):(botData.maxMessageLength*(runs+1))]))
            runs =+ 1
    else:
        await modules.bottiHelper._sendMessage(message, "{}".format(botData.lastError))

async def tts(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl liest eine Nachricht vor.
    !tts {NACHRICHT}
    {NACHRICHT} String
    !tts Ich bin cool
    """
    await modules.bottiHelper._sendTTS(message, message.content[5:])
    await modules.bottiHelper._sendMessagePingAuthor(message, ":robot: Der TTS-Befehl wurde ausgeführt.")
    
    