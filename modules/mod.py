import datetime
import discord
import linecache
import modules.bottiHelper
import modules.data.ids as ids
import os
import xlrd
import xlwt

from time import sleep

async def ban(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl bannt einen Nutzer.
    !ban {@USER}
    {@USER} Nutzer-Erwähnung
    !ban @ETIT-Chef
    """ 
    if len(message.mentions) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "ban"))      
        return      
        
    user = message.mentions[0]
    
    if not await modules.bottiHelper._checkSufficientPrivileges(botti, message, user):
        return
    
    await message.guild.ban(user, reason = "Banned by User-Request.", delete_message_days = 0)
    channel = discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.ALLGEMEIN)
    await channel.trigger_typing()
    await channel.send(":judge: Der Nutzer **{0}#{1}** wurde von {2} gebannt. Der Bann-Hammer hat gesprochen.".format(user.name, user.discriminator, message.author.mention))
    await modules.bottiHelper._sendMessagePingAuthor(message, ":judge: Der Nutzer **{0}#{1}** wurde gebannt.".format(user.name, user.discriminator))

async def chatlog(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl erstellt einen Chatlog.
    !chatlog {AMOUNT}
    {AMOUNT} Integer > 0
    !chatlog 100\r!chatlog
    """ 
    amount = None
    filename = botData.modulesDirectory + "temp/chatlog_" + message.channel.name[1:] + ".txt"
    if " " in message.content:
        try:
            amount = int(message.content.split(" ")[1])
            if amount < 1:
                raise IndexError
        except:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "chatlog"))      
            return  
            
    await modules.bottiHelper._sendMessagePingAuthor(message, ":pencil: Chatlog wird erstellt... Dies kann je nach Anzahl der Nachrichten etwas dauern...\n")
    
    fin = open(filename, "w+", encoding = "utf-8")
    
    count = 0
    async for msg in message.channel.history(limit = amount):
        fin.write("{timestamp} | {author.name}#{author.discriminator} ({author.id}):\n{content}\n\n".format(timestamp = modules.bottiHelper._toUTCTimestamp(msg.created_at), author = msg.author, content = msg.content))
        count += 1
        
    fin.close()
     
    filesize = os.path.getsize(filename)
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":pencil: Chatlog erstellt ({filesize}). Er beinhaltet `{count}` Nachrichten, die zurückreichen bis `{timestamp}`!\n".format(filesize = modules.bottiHelper._convert_byte_sizes(filesize), count = count, timestamp = modules.bottiHelper._toUTCTimestamp(msg.created_at)))
       
    

async def deafen(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl schaltet einen Nutzer taub.
    !deafen {@USER}
    {@USER} Nutzer-Erwähnung
    !deafen @ETIT-Chef
    """
    if len(message.mentions) == 0: 
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "deafen"))      
        return  
    user = message.mentions[0]
    
    if not await modules.bottiHelper._checkSufficientPrivileges(botti, message, user):
        return
    
    if user.voice.deaf is False:
        await user.edit(deafen = True)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":headphones: Der Nutzer {0} wurde **taub** geschaltet.".format(user.mention))
    else:
        await user.edit(deafen = False)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":headphones: Der Nutzer {0} wurde **frei** geschaltet.".format(user.mention))        

async def debugger(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl verleiht/entfernt die Debugger-Rolle.
    !debugger {OPTION} {@USER}
    {OPTION} "add", "remove"
    {@USER} Nutzer-Erwähnung
    !debugger add @ETIT-Chef
    """
    try:
        option = message.content.split(" ")[1]
        user = message.mentions[0]
        if option not in [ "add", "remove" ]:
            raise IndexError("Wrong Parameters.")
    except:    
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "debugger"))      
        return  
      
    debuggerRole = message.guild.get_role(ids.roleIDs.DEBUGGER)
    userRoles = user.roles
    if debuggerRole in userRoles:
        if option == "add":
            await modules.bottiHelper._sendMessagePingAuthor(message, ":fly: {} ist bereits ein Debugger!".format(user.mention))
        else:
            await user.remove_roles(debuggerRole, reason = "Set by {}#{}.".format(message.author.name, str(message.author.discriminator)))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":fly: {} ist jetzt kein Debugger mehr!".format(user.mention))
    else:
        if option == "remove":
            await modules.bottiHelper._sendMessagePingAuthor(message, ":fly: {} ist kein Debugger!".format(user.mention))
        else:
            await user.add_roles(debuggerRole, reason = "Set by {}#{}.".format(message.author.name, str(message.author.discriminator)))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":fly: {} ist jetzt ein Debugger!".format(user.mention))            

async def estimateprunes(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl zeigt die Anzahl der inaktiven Mitglieder seit n Tagen an.
    !estimateprunes {DAYS}
    {DAYS} Ganze Zahl, 30 >= x > 0
    !estimateprunes 2
    """
    try:
        nDays = int(message.content.split(" ")[1])
        if not (nDays in range(1, 31)): # API only allowes days in range(1, 30)
            raise IndexError()
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "estimateprunes"))
        return        
    
    roles = [   message.guild.get_role(ids.roleIDs.ETIT_BSC),
                message.guild.get_role(ids.roleIDs.ETIT_MSC),
                message.guild.get_role(ids.roleIDs.MIT_BSC),
                message.guild.get_role(ids.roleIDs.MIT_MSC),
                message.guild.get_role(ids.roleIDs.KIT_BSC),
                message.guild.get_role(ids.roleIDs.KIT_MSC)
            ]
    estimated_prunes = await message.guild.estimate_pruned_members(days = nDays, roles = roles)
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":stopwatch: **{}** Mitglieder sind seit **{}** Tagen inaktiv.".format(estimated_prunes, nDays))

async def kick(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl kickt einen Nutzer.
    !kick {@USER}
    {@USER} Nutzer-Erwähnung
    !kick @ETIT-Chef
    """
    if len(message.mentions) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "kick"))      
        return  
    user = message.mentions[0]
    
    if not await modules.bottiHelper._checkSufficientPrivileges(botti, message, user):
        return
    
    await message.guild.kick(user, reason="Requestes by Admin.")
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":athletic_shoe: Der Nutzer **{0}#{1}** wurde erfolgreich gekickt.".format(user.name, user.discriminator))

async def listbans(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl listet alle gebannten Nutzer auf.
    !listbans
    """
    bans = await message.guild.bans()
    if len(bans) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":judge: Zurzeit ist niemand gebannt!")
        return
        
    await modules.bottiHelper._sendMessage(message, ":judge: Die folgenden Nutzer sind gebannt {}:".format(message.author.mention))
     
    all_bans = "```\n"
    for entry in bans:
        all_bans += entry.user.name + "#" + entry.user.discriminator + " (ID: " + str(entry.user.id) + ")\n"
    await modules.bottiHelper._sendMessage(message, all_bans + "```")

async def mute(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl schaltet einen Nutzer stumm.
    !mute {@USER}
    {@USER} Nutzer-Erwähnung
    !mute @ETIT-Chef
    """
    if len(message.mentions) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "mute"))      
        return  
    user = message.mentions[0]
    
    if not await modules.bottiHelper._checkSufficientPrivileges(botti, message, user):
        return
    
    if not user.voice.mute:
        await user.edit(mute = True)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":microphone2: Der Nutzer {0} wurde **stumm** geschaltet.".format(user.mention))
    else:
        await user.edit(mute = False)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":microphone2: Der Nutzer {0} wurde **frei** geschaltet.".format(user.mention))

async def newrole(botti, message, botData): 
    """
    Reserviert für Moderator oder höher
    Dieser Befehl erstellt eine neue Rolle.
    !newrole {NAME} {COLOR}
    {NAME} [String]
    {COLOR} [hex]
    !newrole "Test-Rolle" 0x123456
    """
    params = message.content.split(" ")
    if len(params) < 2 or len(message.content.split("\"")) < 2:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "newrole"))      
        return  
        
    try:
        roleColor = int(message.content[-8:], 16)
    except ValueError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "newrole"))      
        return  
        
    roleName = message.content.split("\"")[1]
    
    
    newRole = await message.guild.create_role(name = roleName, color = roleColor)
    
    rolePermissions = discord.PermissionOverwrite.from_pair(allow = discord.Permissions.text(), deny = discord.Permissions.none())

    overwrites = {
        message.guild.default_role: discord.PermissionOverwrite(read_messages = False),
        newRole: rolePermissions
    }
    
    category = discord.utils.get(message.guild.categories, id = ids.categoryIDs.WEITERE_MODULE)
    newChannel = await message.guild.create_text_channel(name = roleName, category = category, overwrites = overwrites)
    await modules.bottiHelper._sendMessagePingAuthor(message, ":white_check_mark: Die Rolle <@&{roleID}>, sowie der Kanal <#{channelID}> wurden erstellt.".format(roleID = newRole.id, channelID = newChannel.id))
    
async def nick(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl ändert den Nickname von einem Nutzer.
    !nick {@USER} {NAME}
    {@USER} Nutzer-Erwähnung
    {NAME} String
    !nick @ETIT-Chef Coolster Bot überhaupt
    """
    user = message.author
    if len(message.mentions) != 0:
        user = message.mentions[0]
    
    if not await modules.bottiHelper._checkSufficientPrivileges(botti, message, user):
        return
    
    nicknameStrings = str(message.content[6:]).split(" ")
    length = len(nicknameStrings)
    nickname = ""
    
    if length == 1:
        await user.edit(nick = "")
        await modules.bottiHelper._sendMessagePingAuthor(message, ":name_badge: Der Nickname von **{0}#{1}** wurde zurückgesetzt.".format(user.name, str(user.discriminator)))
        return
        
    for i in range(1, length):
        nickname = nickname + nicknameStrings[i] + " "
    await user.edit(nick = nickname)
    await modules.bottiHelper._sendMessagePingAuthor(message, ":name_badge: Der Nickname von **{0}#{1}** wurde auf **'{2}'** geändert.".format(user.name, str(user.discriminator), nickname[:-1]))

async def purge(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl löscht Nachrichten.
    !purge {OPTION} {PARAMS}
    {OPTION} x in range(101), "until"
    {PARAMS} <leer>, Message-ID
    !purge 100\r!purge until 832059964651701097
    """
    options = message.content.split(" ")
    if len(options) == 2:
        if (not options[1].isdigit()) or (int(options[1]) not in range(101)):
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "purge")) 
            return
        deleted = await message.channel.purge(limit = int(message.content.split(" ")[1]), check = None)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":recycle: Es wurden **{0}** Nachrichten gelöscht.".format(len(deleted)))
    elif len(options) == 3:
        if (options[1] != "until") or (not options[2].isdigit()):
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "purge")) 
            return
        msg = await message.channel.fetch_message(int(options[2]))
        deleted = await message.channel.purge(after = msg.created_at)
        await modules.bottiHelper._sendMessagePingAuthor(message, ":recycle: Es wurden **{0}** Nachrichten gelöscht.".format(len(deleted)))        
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "purge"))   

async def purgemax(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl löscht alle Befehle in einem Kanal. Dieser Befehl muss bestätigt werden.
    !purgemax
    """
    if not botData.purgemaxConfirm:
        botData.purgemaxConfirm = True
        await modules.bottiHelper._sendMessagePingAuthor(message, ":exclamation: Purgemax eingeleitet! Zum Bestätigen `{prefix}purgemax` erneut eingeben. Zum Abbrechen `{prefix}cancel`. **Bist du dir sicher, was du tust?**".format(prefix = botData.botPrefix))
        return
        
    await modules.bottiHelper._sendMessage(message, ":exclamation: **!Purgemax!**")
    await modules.bottiHelper._sendMessage(message, ":exclamation: **Es werde alle Nachrichten in diesem Kanal gelöscht...**")
    sleep(3)
    delete_int = 0
    run_loop = True
    while run_loop:
        try:
            deleted = await message.channel.purge(limit = 100)
            if len(deleted) == 0:
                run_loop = False
            delete_int += len(deleted)
        except:
            run_loop = False
    
    botData.purgemaxConfirm = False
    await modules.bottiHelper._sendMessagePingAuthor(message, ":recycle: **Purge-Complete**! Es wurden **{0}** Nachrichten gelöscht.".format(delete_int))

async def shoutout(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl verfasst einen Shoutout
    !shoutout {@KANAL} {NACHRICHT}
    {@KANAL} Kanal-Erwähnung
    {NACHRICHT} String
    !shoutout #allgemein Dies ist ein Shoutout
    """
    channelToSend = message.channel
    try:
        if len(message.channel_mentions) != 0:
            channelToSend = message.channel_mentions[0]
            messageToSend = message.content.split(" ")[2]
        else:    
            messageToSend = message.content[10:]
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "shoutout"))      
        return
    await channelToSend.trigger_typing()
    await channelToSend.send(":loudspeaker: {} @everyone\n~ Shoutout von {}".format(messageToSend, message.author.mention))
    await modules.bottiHelper._sendMessagePingAuthor(message, ":loudspeaker: Dein Shoutout wurde gesendet!")  

async def status(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl ändert den Bot-Status
    !status {STATUS} {ICON}
    {STATUS} "" [Zum Zurücksetzen], String
    {ICON} "-dnd", "-idle", "-offline", "-online"
    !status\r!status Ich bin cool\r!status Bitte nicht stören -dnd
    """
    if not "-" in str(message.content):
        if message.content[8:] == "":
        
            await botti.change_presence(activity = discord.Activity(name = botData.botNormalStatus, type = discord.ActivityType.listening), status = discord.Status.online)
            
            await modules.bottiHelper._sendMessagePingAuthor(message, ":information_source: Der Status wurde auf **'" + botData.botNormalStatus + " || online'** zurückgesetzt.")
        else:
            await botti.change_presence(activity = discord.Activity(name = str(message.content[8:]), type = discord.ActivityType.listening), status = discord.Status.online)
            
            await modules.bottiHelper._sendMessagePingAuthor(message, ":information_source: Der Status wurde zu **'{0} || online'** geändert.".format(str(message.content[8:])))
    else:
        status_str = str(message.content).split("-")[1]
        status_game = str(message.content[8:]).replace("-" + status_str, "")
        if status_game == "":
            status_game = botData.botNormalStatus
        status_list = [ "dnd", "idle", "offline", "online"]
        if status_str in status_list:
            await botti.change_presence(activity = discord.Activity(name = status_game, type = discord.ActivityType.listening), status = getattr(discord.Status, status_str))
            
            await modules.bottiHelper._sendMessagePingAuthor(message, ":information_source: Der Status wurde zu **'{0} || {1}'** geändert.".format(status_game, str(getattr(discord.Status, status_str))))
        else:
            
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: **'{0}'** ist kein gültiges Attribut!".format(status_str))

async def unban(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl entbannt einen Nutzer.
    !unban {USER-ID}
    {USER-ID} Nutzer-ID [Gebannte Nutzer können mit !listbans aufgelistet werden]
    !unban 770272473735233587
    """
    userID = str(message.content[7:])
    
    if not userID.isdigit():
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "unban"))      
        return  
    
    bans = await message.guild.bans()
    for entry in bans:
        if entry.user.id == int(userID):
            banned_user_entry = await message.guild.fetch_ban(entry.user)
            
            await message.guild.unban(banned_user_entry.user)
            
            channel = discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.ALLGEMEIN)
            await channel.send(":judge: Der Nutzer **{0}#{1}** wurde von {2} entbannt.".format(banned_user_entry.user.name, banned_user_entry.user.discriminator, message.author.mention))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":judge: Der Nutzer **{0}** wurde entbannt.".format(banned_user_entry.user))
            return 
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Nutzer ist nicht gebannt!")