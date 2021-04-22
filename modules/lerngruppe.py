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
                                            
    await categoryChannel.set_permissions(user, overwrite = overwrites)
    for channel in categoryChannel.channels:
        await channel.set_permissions(user, overwrite = overwrites)
        
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
    
async def _removeUserFromLerngruppe(categoryChannel, message, user, leaveString):
    overwrites = categoryChannel.overwrites
    for overwrite in overwrites:
        if isinstance(overwrite, discord.Member):
            if overwrite.id == user.id:
                del overwrites[overwrite]
                await categoryChannel.edit(overwrite = overwrites)
                for channel in categoryChannel.channels:
                    await channel.edit(overwrites = overwrites)
                await modules.bottiHelper._sendMessage(message, leaveString)
                break
    

async def lerngruppe(botti, message, botData):
    """
    Für alle ausführbar
    Keine Ahnung.
    !lerngruppe
    """
    
    options = [ "create", "delete", "add", "join", "remove", "leave", "makemod" ]
    
    userInput = message.content.split(" ")

    if (not (userInput[1] in options)) or len(userInput) < 2:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
        return 
        
    if userInput[1] == options[0]: # create
        type = "private"
        if len(userInput) > 2:
            if userInput[2] == "public":
                type = "public" 
    
        types = {
            "private": "",
            "public": "[Ö]"
        }
    
        nextFreeID = _getNextFreeID(message)

        userPermissions = discord.PermissionOverwrite.from_pair(allow = discord.Permissions.all(), deny = discord.Permissions.none())
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
    
    elif userInput[1] == options[1]: # delete
        if _isLerngruppenChannel(message.channel.category):
            categoryChannels = message.channel.category.channels
            for channel in categoryChannels:
                await channel.delete()
            await message.channel.category.delete()
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Befehl kann nur in einer Lerngruppe ausgeführt werden!")
    
    elif userInput[1] == options[2]: # add
        if len(message.mentions) == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
            return 
            
        if not (_isLerngruppenChannel(message.channel.category)):    
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Befehl kann nur in einer Lerngruppe ausgeführt werden!")
            return
            
        await _addUserToLerngruppe(message.channel.category, message, message.mentions[0], ":books: {userMention} wurde der Lerngruppe hinzugefügt! {authorMention}".format(userMention = message.mentions[0].mention, authorMention = message.author.mention))
    
    elif userInput[1] == options[3]: # join
        if (len(userInput) < 3) or (not (userInput[2].isdigit())):
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
            return

        id = int(userInput[2])
        
        allChannels = await message.guild.fetch_channels()
        allChannelNames = [channel.name.lower() for channel in allChannels]
        if "[ö] lerngruppe-{id}".format(id = id) in allChannelNames: # If Lerngruppe is public
            for channel in allChannels:
                if "[ö] lerngruppe-{id}".format(id = id) in channel.name.lower():
                    dummyMessage = modules.bottiHelper._createDummyMessage(message.author, channel.text_channels[0])
                    await _addUserToLerngruppe(channel, dummyMessage, message.author, ":books: {userMention} ist der Lerngruppe beigetreten!".format(userMention = message.author.mention))
                    return
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Diese Lerngruppe existiert nicht, oder ist privat!")
    
    elif userInput[1] == options[4]: # remove
        if len(message.mentions) == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "lerngruppe"))      
            return 
            
        if not (_isLerngruppenChannel(message.channel.category)):    
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Befehl kann nur in einer Lerngruppe ausgeführt werden!")
            return
            
        await _removeUserFromLerngruppe(message.channel.category, message, message.mentions[0], ":books: {userMention} wurde aus der Lerngruppe entfernt! {authorMention}".format(userMention = message.mentions[0].mention, authorMention = message.author.mention))
    
    elif userInput[1] == options[5]: # leave
        if not (_isLerngruppenChannel(message.channel.category)):    
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Dieser Befehl kann nur in einer Lerngruppe ausgeführt werden!")
            return
            
        await _removeUserFromLerngruppe(message.channel.category, message, message.author, ":books: {authorMention} hat die Lerngruppe verlassen!".format(authorMention = message.author.mention))
    