import datetime
import discord
import linecache
import os
import platform
import sys
import traceback

from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.utils import manage_commands

from modules.data.botData import botData
import modules.data.ids     as ids

import modules.audio        #as audio
import modules.banlist      #as banlist
import modules.bottiHelper  #as bottiHelper
import modules.dev          #as dev
import modules.gamble       #as gamble
import modules.guard        #as guard
import modules.info         #as info
import modules.lerngruppe   #as lerngruppe
import modules.mensa        #as mensa
import modules.mod          #as mod
import modules.polls        #as polls
import modules.roles        #as roles
import modules.timer        #as timer
import modules.utils        #as utils

bottiIntents = discord.Intents.default()
bottiIntents.members = True
bottiIntents.reactions = True
bottiIntents.presences = False
botti = discord.Client(intents = bottiIntents, guild_subscriptions = True)

slash = SlashCommand(botti, sync_commands = False)
import modules.slash  # MUSS unter der Deklaration und Initialisierung von den Objekten slash und botti stehen
import modules.events # MUSS unter der Deklaration und Initialisierung vom Objekten botti stehen
             
@botti.event
async def on_ready():
    if botData.firstBoot == True:
        modules.bottiHelper._loadSettings(botData)
        botData.totalSlashCommands = len(slash.commands)
        botData.slashCommandList = list(slash.commands)

    data = discord.Embed(
        title = "[:globe_with_meridians:] Online",
        description = "[:shield:] Guard ist aktiv",
        color = 0x00FF00
    )
    data.add_field(name = "API Version", value = modules.bottiHelper._versionInfo())
    data.add_field(name = "Server", value = platform.system() + "-" + str(os.name).upper() + "-" + platform.release())
    data.add_field(name = "Latenz", value = str(round((botti.latency * 1000), 2)) + "ms")
    data.add_field(name = "Intents", value = str(botti.intents).split("=")[1][:-1])
    data.add_field(name = "Nutzer", value = len(botti.users))
    data.add_field(name = "Python Build", value = str(platform.python_build()).replace("'", "").replace("(", "").replace(")", ""))
    data.set_footer(text = "[ID]: {}\nInsgesamt {} Befehle • {} Slash-Befehle!\nGestartet {}".format(str(botti.user.id), str(botData.totalCommands), str(botData.totalSlashCommands), modules.bottiHelper._toSTRFTimestamp(botData.startTimestamp)))
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_author(name = botti.user.name + "#" + botti.user.discriminator, icon_url="https://cdn.discordapp.com/app-assets/" + str(botti.user.id) + "/" + str(ids.assetIDs.profilePicture_AssetID) + ".png")
    
    if botData.firstBoot == True:
        if botData.maintenanceMode is True:
            data.title = "[:globe_with_meridians:] Wartungsarbeiten-Modus"
            data.description = "Verbindung etabliert `@" + modules.bottiHelper._getTimestamp() + "`"
            data.color = 0xFF0000
            await botti.change_presence(activity = discord.Game(name = "⚒ Wartungsarbeiten ⚒"), status = discord.Status.dnd)
        else:
            await modules.bottiHelper._setNormalStatus(botti, botData)
        
            modules.gamble._loadBalancesToKeeper(botti, botData)
            botti.loop.create_task(modules.gamble._saveKeeperToFile(botti, botData))
        
            modules.banlist._loadBotBans(botData)
        
            botti.loop.create_task(modules.mensa._dailyMensa(botti, botData))
        
            #botti.loop.create_task(modules.gamble._cyclicBotDetection(botti, botData, True))
        
        botData.firstBoot = False
    else:
        data.title = "[:globe_with_meridians:] RECONNECT"
        data.description = "Verbindung wurde wiederhergestellt `@" + modules.bottiHelper._getTimestamp() + "`"
        data.color = 0x0000FF
        await modules.bottiHelper._setNormalStatus(botti, botData)
        
    await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.botTestLobby_ChannelID).send(embed = data)

@botti.event
async def on_message(message):
    try:
        # Die Reihenfolge der Abfragen hat einen Grund und sollte nicht geändert werden, um die Funktionlität zu erhalten.
        if message.author == botti.user:
            return
            
        await modules.bottiHelper._checkPingTrigger(message, botti)
        
        if message.content.startswith(botData.botPrefix) is False:
            return
            
        if modules.bottiHelper._logCommand(message, botData) == -1:
            await modules.bottiHelper._sendMessage(message, ":x: Funktionen in DM-Chats nicht verfügbar.")
            return
        
        if await modules.guard._checkBanlist(message, botData) == False:
            return
        
        await modules.guard._floodDetection(message, botti, botData)           
        
        if await modules.bottiHelper._checkCommandIgnoreList(message) == False:
            return
        
        await modules.bottiHelper._checkPurgemaxConfirm(message, botData)
            
        await message.delete()    
        
        if message.author.id not in modules.guard.devIDs and botData.maintenanceMode is True:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":tools: Der Bot befindet sich in Wartungsarbeiten. Bitte versuche es später erneut.")
            return       
                
        command = message.content.lower().split(" ")[0]
        commandName = message.content.lower().split(" ")[0].split("!")[1]
        
        # AUDIO
        if command in botData.audioCommandList:
            if await modules.guard._checkPerms(botti, message, [ ], True ):
                await getattr(modules.audio, commandName)(botti, botData, message)
        # DEV
        elif command in botData.devCommandList:
            if await modules.guard._checkPerms(botti, message, [ ], True ):
                if (message.author.id in modules.guard.trustetIDs) and (command not in [ "!balancekeeper", "!lastcommands", "!commandlist", "!mdtext" ]):
                    await modules.bottiHelper._sendMessagePingAuthor(message, "[:shield:] `Guard`: **Fehlende Berechtigung!**")
                    return
                await getattr(modules.dev, commandName)(botti, message, botData)
        # BANLIST
        elif command in botData.banlistCommandList:
            if await modules.guard._checkPerms(botti, message, [ ] ):
                await getattr(modules.banlist, commandName)(botti, message, botData)
        # GAMBLING
        elif command in botData.gambleCommandList:
            if (message.channel.id != ids.channelIDs.spielhalle_ChannelID) and (command not in [ "!balance", "!rank", "!ranking", "!transfer" ]):
                await modules.bottiHelper._sendMessagePingAuthor(message, ":slot_machine: Dieser Befehl darf nur in <#" + str(ids.channelIDs.spielhalle_ChannelID) + "> verwendet werden!")
                return
            await getattr(modules.gamble, commandName)(botti, message, botData) 
        # INFO
        elif command in botData.infoCommandList:
            await getattr(modules.info, commandName)(botti, message, botData)
        # LERNGRUPPE
        elif command in botData.lerngruppeCommandList:
            await getattr(modules.lerngruppe, commandName)(botti, message, botData)
        # MENSA
        elif command in botData.mensaCommandList:
            await getattr(modules.mensa, commandName)(botti, message, botData)
        # MOD
        elif command in botData.modCommandList:
            if await modules.guard._checkPerms(botti, message, [ "Admin", "Dev", "Fachschaft ETEC", "Tutoren", "Bot-Commander" ] ):
                await getattr(modules.mod, commandName)(botti, message, botData)
        # POLLS
        elif command in botData.pollsCommandList:
            await getattr(modules.polls, commandName)(botti, message, botData)       
        # ROLES
        elif command in botData.rolesCommandList:
            await getattr(modules.roles, commandName)(botti, message, botData)       
        # TIMER
        elif command in botData.timerCommandList:
            await getattr(modules.timer, commandName)(botti, message, botData)       
        # UTILS
        elif command in botData.utilsCommandList:
            await getattr(modules.utils, commandName)(botti, message, botData)                
        elif command == "!cancel":
            pass
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Befehl **'{0}'** existiert nicht!".format(message.content))

        botData.befehlsCounter = botData.befehlsCounter + 1

    except Exception as error:
        botData.lastError = ":warning: Traceback _(Timestamp: {})_  • Verursacht durch {}\n```py\n{}```".format(modules.bottiHelper._getTimestamp(), message.author.mention, traceback.format_exc().replace(os.getcwd()[:-10], ".."))
        await modules.bottiHelper._errorMessage(botti, message, botData, error)

@botti.event
async def on_error(error, *args, **kwargs):
    ex = sys.exc_info()
    fullError = ""
    for i in traceback.format_exception(ex[0], ex[1], ex[2]):
        fullError = fullError + i.replace(os.getcwd()[:-10], "..")
        
    fullError = fullError.replace("..", "").replace("```", "´´´")

    botData.lastError = ":warning: Error in `{}()` • Traceback _(Timestamp: {})_\n```py\n{}```".format(error, modules.bottiHelper._getTimestamp(), fullError)
    
    if len(botData.lastError) > 1900:
        await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.botTestLobby_ChannelID).send(content = "{}".format(botData.lastError.split("\n")[0]))
        longError = botData.lastError[(len(botData.lastError.split("\n")[0])):]
        j = 0
        markdownAppend = ""
        for i in range(0, len(botData.lastError), 1900):
            if j > 0:
                markdownAppend = "```py\n"
            await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.botTestLobby_ChannelID).send(content = "{}{}```".format(markdownAppend, longError[(1900*j):(1900*(j+1))]))
            j =+ 1
    else:    
        pass
        await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.botTestLobby_ChannelID).send(content = botData.lastError)

botti.run(botData.botToken)
