import discord
import modules.bottiHelper
import modules.data.ids as ids
from random import randint

async def _addUserToLerngruppe(categoryChannel, message, user, joinString):
    overwrites = discord.PermissionOverwrite(   read_messages = True, 
                                                send_messages = True,
                                                manage_messages = True,                                                                           
                                                embed_links = True, 
                                                attach_files = True,
                                                read_message_history = True,
                                                external_emojis = True,
                                                connect = True,
                                                speak = True
                                            )
                                            
    await _overwritePermissionsForUser(categoryChannel, user, overwrites)
        
    await modules.bottiHelper._sendMessage(message, joinString)
    
def _getNextFreeID(message):
    ids = []
    for categoryChannel in message.guild.categories:
        if _isLerngruppenChannel(categoryChannel):
            ids.append(int(categoryChannel.name.split("-")[1]))
            
    ids = sorted(ids)
    runs = 0
    for id in ids:
        if id > runs:
            break
        runs += 1    
    
    return runs           

def _isLerngruppenChannel(categoryChannel):
    if "lerngruppe" in categoryChannel.name.lower():
        try: # If there is another channel with "lerngruppe" in its name, but has no ID
            id = int(categoryChannel.name.split("-")[1]) 
            if id >= 0:
                return True
        except:
            pass
    return False
 
def _isModUser(categoryChannel, user):
    userPermissions = categoryChannel.permissions_for(user)
    
    return userPermissions.manage_webhooks
 
async def _overwritePermissionsForUser(categoryChannel, user, overwrites):    
    await categoryChannel.set_permissions(user, overwrite = overwrites)
    for channel in categoryChannel.channels:
        await channel.set_permissions(user, overwrite = overwrites)
        
async def _removeUserFromLerngruppe(categoryChannel, message, user, leaveString):
    await _overwritePermissionsForUser(categoryChannel, user, None)
    await modules.bottiHelper._sendMessage(message, leaveString)
    
async def _sendMessageNoLerngruppenChannel(message):
    await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Befehl kann nur in einer Lerngruppe ausgeführt werden!")
            
async def _sendMessageNoPermissions(message):
    await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du bist kein Moderator dieser Lerngruppe, darfst diesen Befehl also nicht ausführen!")
                        
async def _subcommandAddUser(message, botData):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return
    
    if not (_isModUser(message.channel.category, message.author)):
        await _sendMessageNoPermissions(message)
        return
    
    if len(message.mentions) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return 
        
    await _addUserToLerngruppe(message.channel.category, message, message.mentions[0], ":books: {userMention} wurde der Lerngruppe hinzugefügt! {authorMention}".format(userMention = message.mentions[0].mention, authorMention = message.author.mention))

async def _subcommandCreateLerngruppe(message, userInput):
    types = {
        "private": "",
        "public": "[Ö]"
    }
    
    type = "private"
    if len(userInput) > 2:
        if userInput[2] == "public":
            type = "public" 

    nextFreeID = _getNextFreeID(message)

    userPermissions = discord.PermissionOverwrite.from_pair(allow = discord.Permissions.all(), deny = discord.Permissions.none())
    userPermissions.update(manage_channels = False)
    userPermissions.update(manage_permissions = False)

    overwrites = {
        message.guild.default_role: discord.PermissionOverwrite(read_messages = False),
        message.author : userPermissions
    }
       
    newCategory = await message.guild.create_category(name = "{type} Lerngruppe-{id}".format(type = types[type], id = nextFreeID), overwrites = overwrites)
    newChannel = await message.guild.create_text_channel(name = "📚Lerngruppe-{id}".format(id = nextFreeID), category = newCategory)
    await message.guild.create_voice_channel(name = "📚Lerngruppe-{id}".format(id = nextFreeID), category = newCategory)
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Deine Lerngruppe _(mit der ID: {id})_ wurde erstellt!".format(id = nextFreeID))
    await newChannel.send(":books: Lerngruppe-{id} {type}\n:books: Eigentümer: {owner}\n:books: Erstellt: {created}".format(id = nextFreeID, type = types[type], owner = message.author.mention, created = modules.bottiHelper._getTimestamp()))
    
async def _subcommandDelete(message):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return
    
    if not (_isModUser(message.channel.category, message.author)):
        await _sendMessageNoPermissions(message)
        return
        
    categoryChannels = message.channel.category.channels
    for channel in categoryChannels:
        await channel.delete()
    await message.channel.category.delete()
    
async def _subcommandJoin(message, userInput, botData):
    if (len(userInput) < 3) or (not (userInput[2].isdigit())):
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return

    id = int(userInput[2])
    
    allChannels = await message.guild.fetch_channels()
    allChannelNames = [channel.name.lower() for channel in allChannels]
    if "[ö] lerngruppe-{id}".format(id = id) in allChannelNames: # If Lerngruppe is public
        for channel in allChannels:
            if "[ö] lerngruppe-{id}".format(id = id) in channel.name.lower():
                dummyMessage = modules.construct._constructDummyMessage(message.author, channel.text_channels[0])
                await _addUserToLerngruppe(channel, dummyMessage, message.author, ":books: {userMention} ist der Lerngruppe beigetreten!".format(userMention = message.author.mention))
                return
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Diese Lerngruppe existiert nicht, oder ist privat!")
 
async def _subcommandLeave(message):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return
        
    await _removeUserFromLerngruppe(message.channel.category, message, message.author, ":books: {authorMention} hat die Lerngruppe verlassen!".format(authorMention = message.author.mention))

async def _subcommandMakemod(message):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return
    
    if not (_isModUser(message.channel.category, message.author)):
        await _sendMessageNoPermissions(message)
        return
    
    if len(message.mentions) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return 
    
    userPermissions = discord.PermissionOverwrite.from_pair(allow = discord.Permissions.all(), deny = discord.Permissions.none())
    userPermissions.manage_channels = False
    userPermissions.manage_permissions = False

    await _overwritePermissionsForUser(message.channel.category, message.mentions[0], userPermissions)
    await modules.bottiHelper._sendMessagePingAuthor(message, ":books: {newModMention} ist jetzt Moderator dieser Lerngruppe!".format(newModMention = message.mentions[0].mention))
 
async def _subcommandPromote(message, botData):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return
    
    if not (_isModUser(message.channel.category, message.author)):
        await _sendMessageNoPermissions(message)
        return
    
    if not ("[ö]" in message.channel.category.name.lower()):
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Deine Lerngruppe ist nicht öffentlich! Du kannst sie deshalb nicht bewerben!")
        return
        
    if message.channel.topic == None:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Die Lerngruppe benötigt eine Beschreibung, um sie zu bewerben. Nutze `{prefix}lerngruppe setdescription <Beschreibung>` um eine zu setzen!".format(prefix = botData.botPrefix))
        return
        
    channel = message.guild.get_channel(ids.channelIDs.LERNGRUPPE_FINDEN)
    id = int(message.channel.category.name.split("-")[1])
    
    botMessage = await channel.send(":books: {authorMention} bewirbt **{promotedChannel}**:\n```\n{description}``` Trete mit `{prefix}lerngruppe join {id}`, oder indem du mit {emoji} reagierst, bei!".format(authorMention = message.author.mention, promotedChannel = message.channel.category.name.split(" ")[1], description = message.channel.topic, prefix = botData.botPrefix, id = id, emoji = modules.construct._constructEmojiString(ids.emojiIDs.APPROVE)))
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.APPROVE))
 
async def _subcommandRemove(message):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return
    
    if not (_isModUser(message.channel.category, message.author)):
        await _sendMessageNoPermissions(message)
        return
    
    if len(message.mentions) == 0:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return 
        
    await _removeUserFromLerngruppe(message.channel.category, message, message.mentions[0], ":books: {userMention} wurde aus der Lerngruppe entfernt! {authorMention}".format(userMention = message.mentions[0].mention, authorMention = message.author.mention))

async def _subcommandSetdescription(message, userInput):
    if not (_isLerngruppenChannel(message.channel.category)):    
        await _sendMessageNoLerngruppenChannel(message)
        return    
     
    if not (_isModUser(message.channel.category, message.author)):
        await _sendMessageNoPermissions(message)
        return
     
    if len(userInput) < 3:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return
        
    description = message.content[27:] # 27 = len("!lerngruppe setdescription ")
 
    for textChannel in message.channel.category.text_channels:
        await textChannel.edit(topic = description)
        
    await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Die Beschreibung der Lerngruppe wurde auf **\"{description}\"** gesetzt!".format(description = description))
 
async def lerngruppe(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl verwaltet alles was mit Lerngruppen zu tun hat.
    !lerngruppe {OPTION} {ARGS}
    {OPTION} "create", "delete", "add", "join", "remove", "leave", "makemod", "setdescription"
    {ARGS} <leer>, Nutzer-Erwänung, Lerngruppen-ID, Beschreibung [String]
    !lerngruppe create\r!lerngruppe join 0\r!lerngruppe remove @ETIT-Chef
    """
    
    options = [ "create", "delete", "add", "join", "remove", "leave", "makemod", "setdescription", "promote" ]
    
    userInput = message.content.split(" ")

    if (len(userInput) < 2) or (not (userInput[1] in options)):
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return 

    functionDict = {
        options[0]: {
            "func": _subcommandCreateLerngruppe,
            "args": [ message, userInput ]
        },
        options[1]: {
            "func": _subcommandDelete,
            "args": [ message ]
        },
        options[2]: {
            "func": _subcommandAddUser,
            "args": [ message, botData ]
        },
        options[3]: {
            "func": _subcommandJoin,
            "args": [ message, userInput, botData ]
        },
        options[4]: {
            "func": _subcommandRemove,
            "args": [ message ]
        },
        options[5]: {
            "func": _subcommandLeave,
            "args": [ message ]
        },
        options[6]: {
            "func": _subcommandMakemod,
            "args": [ message ]
        },
        options[7]: {
            "func": _subcommandSetdescription,
            "args": [ message, userInput ]
        },
        options[8]: {
            "func": _subcommandPromote,
            "args": [ message, botData ]
        }
    }
    
    func = functionDict[userInput[1]]["func"]
    args = functionDict[userInput[1]]["args"]
    
    await func(*args)