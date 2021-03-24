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
botti = discord.Client(intents = bottiIntents, guild_subscriptions = True)

slash = SlashCommand(botti, sync_commands = False)
    
@botti.event
async def on_member_join(member):
    roles = []
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    roles.append(guild.get_role(ids.roleIDs.ETIT_Ersti_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Freizeit_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Nicht_Vorgestellt_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Zitate_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Musik_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Memes_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Gaming_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Katzen_RoleID))
    roles.append(guild.get_role(ids.roleIDs.tech_talk_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Spielhalle_RoleID))
    roles.append(guild.get_role(ids.roleIDs.Vorlesungsspam_RoleID))
    await member.edit(roles = roles, reason = "Mitglieder beitritt.")

@botti.event
async def on_raw_reaction_add(payload): 
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    
    # Vorschlag
    if payload.channel_id == ids.channelIDs.dm_itzFlubby_ChannelID and payload.user_id == ids.userIDs.itzFlubby_ID:
        if botti.get_user(ids.userIDs.itzFlubby_ID).dm_channel is None:
            await botti.get_user(ids.userIDs.itzFlubby_ID).create_dm()
        vorschlagMessage = (await botti.get_user(ids.userIDs.itzFlubby_ID).dm_channel.fetch_message(payload.message_id)).content
        channel_botTestLobby_ChannelID = guild.get_channel(ids.channelIDs.botTestLobby_ChannelID)
        updatedStatus = ""
        if payload.emoji.name == "✅":
            updatedStatus = "angenommen"
        elif payload.emoji.name == "➖":
             updatedStatus = "ignoriert"
        elif payload.emoji.name == "❌":
             updatedStatus = "abgelehnt"
        await channel_botTestLobby_ChannelID.send(":bookmark_tabs: Statusänderung für Vorschlag von {0} ({1}) <@!{1}> `@{2}`\n`{3}`\nwurde auf {4} **{5}** gesetzt!".format(vorschlagMessage.split(" ")[0], vorschlagMessage.split(" ")[1][1:-1], vorschlagMessage.split("| ")[1], vorschlagMessage.split("'")[1], payload.emoji.name, updatedStatus)) 

    # ROLLEN
    if payload.message_id == ids.messageIDs.roleSelect_MessageID:
        if payload.emoji.name == "⚡":
            userRoles = modules.roles._changeRole(payload.member.roles, [                                ids.roleIds.MIT_Ersti_RoleID, ids.roleIds.Info_RoleID, ids.roleIds.Paedagogik_RoleID, ids.roleIds.NWT_RoleID, ids.roleIds.Gast_RoleID ], guild.get_role(ids.roleIds.ETIT_Ersti_RoleID), guild)
        elif payload.emoji.name == "⚙️":
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIds.ETIT_Ersti_RoleID,                               ids.roleIds.Info_RoleID, ids.roleIds.Paedagogik_RoleID, ids.roleIds.NWT_RoleID, ids.roleIds.Gast_RoleID ], guild.get_role(ids.roleIds.MIT_Ersti_RoleID), guild)
        elif payload.emoji.name == "💻":
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIds.ETIT_Ersti_RoleID, ids.roleIds.MIT_Ersti_RoleID,                          ids.roleIds.Paedagogik_RoleID, ids.roleIds.NWT_RoleID, ids.roleIds.Gast_RoleID ], guild.get_role(ids.roleIds.Info_RoleID), guild)
        elif payload.emoji.name == "👦":
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIds.ETIT_Ersti_RoleID, ids.roleIds.MIT_Ersti_RoleID, ids.roleIds.Info_RoleID,                                ids.roleIds.NWT_RoleID, ids.roleIds.Gast_RoleID ], guild.get_role(ids.roleIds.Paedagogik_RoleID), guild)
        elif payload.emoji.name == "👨‍🏫":
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIds.ETIT_Ersti_RoleID, ids.roleIds.MIT_Ersti_RoleID, ids.roleIds.Info_RoleID, ids.roleIds.Paedagogik_RoleID,                         ids.roleIds.Gast_RoleID ], guild.get_role(ids.roleIds.NWT_RoleID), guild)
        elif payload.emoji.name == "👤":
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIds.ETIT_Ersti_RoleID, ids.roleIds.MIT_Ersti_RoleID, ids.roleIds.Info_RoleID, ids.roleIds.Paedagogik_RoleID, ids.roleIds.NWT_RoleID                          ], guild.get_role(ids.roleIds.Gast_RoleID), guild)
        else:
            return
        await payload.member.edit(roles = userRoles, reason = "Requested by user.")
        
    if payload.message_id == ids.messageIDs.removeRoleSelect_MessageID:
        if payload.emoji.name == "💬":
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Zitate_RoleID ], -1, guild)
        elif payload.emoji.name == "🎼":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Musik_RoleID ], -1, guild)          
        elif payload.emoji.name == "👾":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Memes_RoleID ], -1, guild)       
        elif payload.emoji.name == "🎮":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Gaming_RoleID ], -1, guild)       
        elif payload.emoji.name == "😺":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Katzen_RoleID ], -1, guild)       
        elif payload.emoji.name == "💻":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.tech_talk_RoleID ], -1, guild)       
        elif payload.emoji.name == "🎰":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Spielhalle_RoleID ], -1, guild)       
        elif payload.emoji.name == "🐖":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Vorlesungsspam_RoleID ], -1, guild)       
        elif payload.emoji.name == "❌":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Zitate_RoleID, ids.roleIDs.Musik_RoleID, ids.roleIDs.Memes_RoleID, ids.roleIDs.Gaming_RoleID, ids.roleIDs.Katzen_RoleID, ids.roleIDs.tech_talk_RoleID, ids.roleIDs.Spielhalle_RoleID, ids.roleIDs.Vorlesungsspam_RoleID, ids.roleIDs.Freizeit_RoleID ], -1, guild)          
        else:
            return
        await payload.member.edit(roles = userRoles, reason = "Requested by user.")  
        
    if payload.message_id == ids.messageIDs.matlabSelect_MessageID:
        try:
            await payload.member.add_roles(guild.get_role(ids.roleIDs.Matlab_RoleID), reason = "Requested by user.")
        except:
            pass
   
    # DANKE               
    if payload.emoji.id == ids.emojiIDs.danke_EmojiID:
        channel = payload.member.guild.get_channel(payload.channel_id)
        helpfulMessage = await channel.fetch_message(payload.message_id)
        if payload.user_id == helpfulMessage.author.id:
            await helpfulMessage.add_reaction("❌")
            return
        
        reactions = helpfulMessage.reactions
        wasAcknowledged = False
        for reaction in reactions:
            try:
                if reaction.me == True:
                    wasAcknowledged = True
            except:
                pass
                
        if wasAcknowledged == False:
            if modules.gamble._getBalance(botData, helpfulMessage.author.id) == -1:
                modules.gamble._createAccount(botData, helpfulMessage.author.id)
                
            if helpfulMessage.author.id != ids.userIDs.itzFlubby_ID:
                modules.gamble._setBalance(botData, helpfulMessage.author.id, 1500)
                
            await helpfulMessage.add_reaction("✅")
        pass
              
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
        
        if message.content.startswith(botData.botPrefix) is not True:
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
            if await modules.guard._checkPerms(botti, message, [ ] ):
                if (message.author.id == ids.userIDs.Christoph_ID) and (command not in [ "!balancekeeper", "!lastcommands", "!commandlist" ]):
                    await modules.bottiHelper._sendMessagePingAuthor(message, "[:shield:] `Guard`: **Fehlende Berechtigung!**")
                    return
                await getattr(modules.dev, commandName)(botti, message, botData)
        # BANLIST
        elif command in botData.banlistCommandList:
            if await modules.guard._checkPerms(botti, message, [ ] ):
                await getattr(modules.banlist, commandName)(botti, message, botData)
        # GAMBLING
        elif command in botData.gambleCommandList:
            if (message.channel.id != ids.channelIDs.spielhalle_ChannelID) and (command not in [ "!balance", "!ranking", "!transfer" ]):
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

@slash.slash(name="convert", description="Konvertiert einen Inhalt.", options = [ manage_commands.create_option(
    name = "typ",
    description = "Hier kannst du auswählen, wonach dein Inhalt konvertiert werden soll.",
    option_type = 3,
    choices = [ {
            "name": "Text zu Binär", 
            "value": "text bin"
        }, {
            "name": "Binär zu Text", 
            "value": "bin text"
        }, {
            "name": "Text zu Hex", 
            "value": "text hex"
        }, {
            "name": "Hex zu Text", 
            "value": "hex text"
        }, {
            "name": "Binär zu Hex", 
            "value": "bin hex"
        }, {
            "name": "Hex zu Binär", 
            "value": "hex bin"
        } ],
    required = True ),
    manage_commands.create_option(
    name = "inhalt",
    description = "Inhalt zum Konvertieren.",
    option_type = 3,
    required = True )])
async def _convert(ctx, typ, inhalt):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "!convert " + typ + " " + inhalt)
    await ctx.send(content = "Slash-Command: Convert")
    await modules.utils.convert(botti, msg, botData)

@slash.slash(name="klausuren", description="Zeigt die anstehenden Klausuren an.")
async def _klausuren(ctx: SlashContext):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    await ctx.send(content = "Slash-Command: Klausuren")   
    await modules.utils.klausuren(botti, msg, botData)    

@slash.slash(name="mensa", description="Zeigt den Speiseplan an.", options = [ manage_commands.create_option(
    name = "mensa",
    description = "Optional kannst du hier eine Mensa auswählen. Standard: Mensa am Adenauerring.",
    option_type = 3,
    choices = [ {
            "name": "Am Adenauerring", 
            "value": "adenauerring"
        }, {
            "name": "Erzbergstraße", 
            "value": "erzberger"
        }, {
            "name": "Schloss Gottesaue", 
            "value": "gottesaue"
        }, {
            "name": "Tiefbronner Straße", 
            "value": "tiefenbronner"
        }, {
            "name": "Caféteria Moltkestraße 30",
            "value": "x1moltkestrasse"
    } ],
    required = False ),
    manage_commands.create_option(
    name = "wochentag",
    description = "Optional kannst du hier den gewünschten Wochentag angeben. Standard: Morgen.",
    option_type = 3,
    choices = [ {
            "name": "Montag", 
            "value": "mo"
        }, {
            "name": "Dienstag", 
            "value": "di"
        }, {
            "name": "Mittwoch", 
            "value": "mi"
        }, {
            "name": "Donnerstag", 
            "value": "do"
        }, {
            "name": "Freitag", 
            "value": "fr"
        } ],
    required = False )])
async def _mensa(ctx, mensa = "adenauerring", wochentag = "none"):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    commandArgs = "!mensa " + mensa + " "
    if wochentag != "none":
        commandArgs = commandArgs + wochentag
    
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, commandArgs)
    await ctx.send(content = "Slash-Command: Mensa")
    await modules.mensa.mensa(botti, msg, botData)

@slash.slash(name="ping", description="Gibt die Discord-WebSocket-Latenz an.")
async def _ping(ctx: SlashContext):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    await ctx.send(content = ":satellite: Die Discord WebSocket-Protokoll-Latenz liegt bei **{0}ms**!".format(str(round((botti.latency * 1000), 2))), hidden = True) 

@slash.slash(name="templerngruppe", description="Erstellt oder verwaltet eine temporäre Lerngruppe", options = [ manage_commands.create_option(
    name = "option",
    description = "Optional kannst du hier Verwaltungbefehle eingeben.",
    option_type = 3,
    choices = [ {
            "name": "add", 
            "value": "add"
        }, {
            "name": "delete", 
            "value": "delete"
        }],
    required = False ),
    manage_commands.create_option(
    name = "user",
    description = "Optional kannst du hier einen Nutzer zum Hinzufügen angeben.",
    option_type = 6,
    required = False )])
async def _templerngruppe(ctx: SlashContext, option = "", user = None):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    commandArgs = " "
    if option == "":
        commandArgs = ""
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "!templerngruppe" + commandArgs + option)
    if user != "":
        msg.mentions = [ user ]
    await ctx.send(content = "Slash-Command: Templerngruppe")
    await modules.lerngruppe.templerngruppe(botti, msg, botData)

@slash.slash(name="test", description="Überprüft, ob einfach alles funzt...")
async def _test(ctx: SlashContext):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    msg = await ctx.send(content = ":globe_with_meridians: Der Bot ist online und läuft ordnungsgemäß!", hidden = True) 

@slash.slash(name="userinfo", description="Zeigt Informationen über einen Benutzer an!", options = [ manage_commands.create_option(
    name = "benutzer",
    description = "Hier musst du einen Benutzer auswählen.",
    option_type = 6,
    required = True )])
async def _userinfo(ctx, benutzer):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    msg.mentions = [ benutzer ]
    await ctx.send(content = "Slash-Command: Userinfo")
    await modules.info.userinfo(botti, msg, botData)

@slash.slash(name="vorschlag", description="Sag mir deine Meinung! Gebe Verbesserungsvorschläge, oder -ideen ab!", options = [ manage_commands.create_option(
    name = "nachricht",
    description = "Hier kannst du deine Meinung reinschreiben. Bitte sei nicht zu böse :) !",
    option_type = 3,
    required = True )])
async def _vorschlag(ctx: SlashContext, nachricht): #id 799724675655270420
    modules.bottiHelper._logSlashCommand(ctx, botData)   
    if botti.get_user(ids.userIDs.itzFlubby_ID).dm_channel is None:
        await botti.get_user(ids.userIDs.itzFlubby_ID).create_dm()
    sentMessage = await botti.get_user(ids.userIDs.itzFlubby_ID).dm_channel.send("**{0}#{1}** ({2}) hat per SlashCommand folgendes vorgeschlagen: _'{3}'_. | {4}".format(ctx.author.name, ctx.author.discriminator, ctx.author.id, nachricht, modules.bottiHelper._getTimestamp()))
    await sentMessage.add_reaction("✅")
    await sentMessage.add_reaction("➖")
    await sentMessage.add_reaction("❌")

    await ctx.send(content = ":bookmark_tabs: Deine Nachricht wurde erfolgreich zugestellt!", hidden = True) 

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

@botti.event
async def on_slash_command_error(ctx, ex):
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    fullError = ""
    for i in traceback.format_exception(type(ex), ex, ex.__traceback__):
        fullError = fullError + i.replace(os.getcwd()[:-10], "..")
        
    botData.lastError = ":warning: Traceback _(Timestamp: {})_  • Verursacht durch {} [via Slash-Command]\n```py\n{}```".format(modules.bottiHelper._getTimestamp(), msg.author.mention, fullError)
    await modules.bottiHelper._errorMessage(botti, msg, botData, ex)

botti.run(botData.botToken)
