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

bottiIntents = discord.Intents.default()
bottiIntents.members = True
bottiIntents.reactions = True
bottiIntents.presences = False
botti = discord.Client(intents = bottiIntents, guild_subscriptions = True)

from modules.data.botData import botData
import modules.data.ids     as ids

import modules.audio
import modules.banlist
import modules.bottiHelper
import modules.calendar
import modules.dev
import modules.gamble
import modules.guard
import modules.info
import modules.lerngruppe
import modules.mensa
import modules.mod
import modules.newLectureVideoCheck # MUSS unter der Deklaration und Initialisierung vom Objekten botti stehen
import modules.polls
import modules.timer
import modules.utils

slash = SlashCommand(botti, sync_commands = True)
import modules.slash  # MUSS unter der Deklaration und Initialisierung von den Objekten slash und botti stehen
import modules.events # MUSS unter der Deklaration und Initialisierung vom Objekten botti stehen

from modules.data.commandModule import commandModule             
             
@botti.event
async def on_ready():

    if botData.firstBoot:
        modules.bottiHelper._loadSettings(botData)
        botData.totalSlashCommands = len(slash.commands)
        botData.slashCommandList = list(slash.commands)

    data = discord.Embed(
        title = "[{emoji}] Online".format(emoji = modules.bottiHelper._constructEmojiString(ids.emojiIDs.ONLINE)),
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
    data.set_author(name = botti.user.name + "#" + botti.user.discriminator, icon_url="https://cdn.discordapp.com/app-assets/" + str(botti.user.id) + "/" + str(ids.assetIDs.PROFILE_PICTURE) + ".png")
    
    if botData.firstBoot:
        if botData.maintenanceMode:
            data.title = "[{emoji}] Wartungsarbeiten-Modus".format(emoji = modules.bottiHelper._constructEmojiString(ids.emojiIDs.DND))
            data.description = "Verbindung etabliert `@" + modules.bottiHelper._getTimestamp() + "`"
            data.color = 0xFF0000
            await botti.change_presence(activity = discord.Game(name = "⚒ Wartungsarbeiten ⚒"), status = discord.Status.dnd)
            
            botti.loop.create_task(modules.newLectureVideoCheck._cyclicNewLectureVideoCheck())
        else:
            await modules.bottiHelper._setNormalStatus(botti, botData)
        
            modules.gamble._loadBalancesToKeeper(botti, botData)
            botti.loop.create_task(modules.gamble._saveKeeperToFile(botti, botData))
        
            modules.banlist._loadBotBans(botData)
        
            botti.loop.create_task(modules.mensa._dailyMensa(botti, botData))
            
            botti.loop.create_task(modules.newLectureVideoCheck._cyclicNewLectureVideoCheck())
        
            #botti.loop.create_task(modules.gamble._cyclicBotDetection(botti, botData, True))
            
        botData.firstBoot = False
    else:
        data.title = "[{emoji}] RECONNECT".format(emoji = modules.bottiHelper._constructEmojiString(ids.emojiIDs.ONLINE))
        data.description = "Verbindung wurde wiederhergestellt `@" + modules.bottiHelper._getTimestamp() + "`"
        data.color = 0x0000FF
        await modules.bottiHelper._setNormalStatus(botti, botData)
        
    await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.BOT_TEST_LOBBY).send(embed = data)

@botti.event
async def on_message(message):
    try:
        # Die Reihenfolge der Abfragen hat einen Grund und sollte nicht geändert werden, um die Funktionlität zu erhalten.
        if message.author == botti.user:
            return
            
        if message.channel.type == discord.ChannelType.private:
            userDM = await modules.bottiHelper._createDM(botti, ids.userIDs.ITZFLUBBY)
            await userDM.send("**{author.name}#{author.discriminator}** ({author.id}) hat im Privat-Chat folgendes geschrieben: _'{content}'_. | {timestamp}".format(author = message.author, content = message.content, timestamp = modules.bottiHelper._getTimestamp()))
            
            
        await modules.bottiHelper._checkPingTrigger(botti, botData, message)
        
        if not message.content.startswith(botData.botPrefix):
            return
            
        if modules.bottiHelper._logCommand(message, botData) == -1:
            await modules.bottiHelper._sendMessage(message, ":x: Funktionen in DM-Chats nicht verfügbar.")
            return
        
        if not await modules.guard._checkBanlist(message, botData):
            return
        
        await modules.guard._floodDetection(message, botti, botData)           
        
        if not await modules.bottiHelper._checkCommandIgnoreList(message):
            return
        
        await modules.bottiHelper._checkPurgemaxConfirm(message, botData)
            
        await message.delete()    
        
        if (message.author.id not in modules.guard.devIDs) and botData.maintenanceMode:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":tools: Der Bot befindet sich in Wartungsarbeiten. Bitte versuche es später erneut.")
            return       
                
        command = message.content.lower().split(" ")[0][1:]
        
        for module in botData.allCommandModules:
            if command in module.commandNameList:
                # BEGIN SPECIAL CASES #
                if (module.module is modules.gamble) and (command not in [ "balance", "rank", "ranking", "transfer" ]) and (message.channel.id != ids.channelIDs.SPIELHALLE):
                    await modules.bottiHelper._sendMessagePingAuthor(message, ":slot_machine: Dieser Befehl darf nur in <#{channelID}> verwendet werden!".format(channelID = ids.channelIDs.SPIELHALLE))
                    return
                # END SPECIAL CASES #
                if 0 not in module.allowedRoles:
                    if not await modules.guard._checkPerms(botti, message, module.allowedRoles, module.enableTrustet ):
                        return
                await getattr(module.module, command)(botti, message, botData)
                botData.befehlsCounter += 1
                return
                
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Befehl **'{0}'** existiert nicht!".format(message.content))        
    except Exception as error:
        botData.lastError = ":warning: Traceback _(Timestamp: {})_  • Verursacht durch {}\n```py\n{}```".format(modules.bottiHelper._getTimestamp(), message.author.mention, traceback.format_exc().replace(os.getcwd()[:-10], ".."))
        await modules.bottiHelper._errorMessage(botti, message, botData, error)

@botti.event
async def on_error(error, *args, **kwargs):
    ex = sys.exc_info()
    fullError = ""
    for i in traceback.format_exception(ex[0], ex[1], ex[2]):
        fullError += i.replace(os.getcwd()[:-10], "..")
        
    fullError = fullError.replace("..", "").replace("```", "´´´")

    botData.lastError = ":warning: Error in `{}()` • Traceback _(Timestamp: {})_\n```py\n{}```".format(error, modules.bottiHelper._getTimestamp(), fullError)
    
    if len(botData.lastError) > botData.maxMessageLength:
        j = 0
        for i in range(0, len(botData.lastError), botData.maxMessageLength):
            await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.BOT_TEST_LOBBY).send(content = "```py\n{}```".format(botData.lastError[(botData.maxMessageLength*j):(botData.maxMessageLength*(j+1))]))
            j =+ 1
    else:    
        await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.BOT_TEST_LOBBY).send(content = botData.lastError)

botti.run(botData.botToken)
