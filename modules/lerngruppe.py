import discord
import modules.bottiHelper
import modules.data.ids as ids
from random import randint

async def lerngruppe(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl fügt dich einer Lerngruppe hinzu.
    !lerngruppe {LERNGRUPPE}
    {LERNGRUPPE} 1 - 10
    !lerngruppe 3
    """
    roleNumbers = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "10" ]
    for i in range(0, len(roleNumbers)):
        if str(message.content[12:]) == roleNumbers[i]:
            userRoles = message.author.roles
            for j in range(0, len(userRoles) - 1):
                if "Lerngruppe " in userRoles[j].name:
                    await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Da du dich bereits in der **{0}** befindest und nicht in mehreren gleichzeitig sein kannst, wirst du zuerst aus dieser entfernt.".format(userRoles[j].name))
                    del userRoles[j]
            roleIds = [ ids.roleIDs.Lerngruppe1_RoleID, ids.roleIDs.Lerngruppe2_RoleID, ids.roleIDs.Lerngruppe3_RoleID, ids.roleIDs.Lerngruppe4_RoleID, ids.roleIDs.Lerngruppe5_RoleID, ids.roleIDs.Lerngruppe6_RoleID, ids.roleIDs.Lerngruppe7_RoleID, ids.roleIDs.Lerngruppe8_RoleID, ids.roleIDs.Lerngruppe9_RoleID,ids.roleIDs.Lerngruppe10_RoleID ]
            userRoles.append(message.guild.get_role(roleIds[i]))
            await message.author.edit(roles=userRoles)
            
            await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Du bist der **Lerngruppe {0}** beigetreten!".format(message.content[12:]))
            return
    await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!lerngruppe"))  
 
async def listlerngruppen(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl listet alle Lerngruppen auf.
    !listlerngruppen
    """
    data =  discord.Embed(
        title = "",
        color = 0x005dff,
        description = "Mitglieder-Verteilung"
    ) 
    roleIds = [ ids.roleIDs.Lerngruppe1_RoleID, ids.roleIDs.Lerngruppe2_RoleID, ids.roleIDs.Lerngruppe3_RoleID, ids.roleIDs.Lerngruppe4_RoleID, ids.roleIDs.Lerngruppe5_RoleID, ids.roleIDs.Lerngruppe6_RoleID, ids.roleIDs.Lerngruppe7_RoleID, ids.roleIDs.Lerngruppe8_RoleID, ids.roleIDs.Lerngruppe9_RoleID,ids.roleIDs.Lerngruppe10_RoleID ]
    for i in range(len(roleIds)):        
        data.add_field(name = "Lerngruppe " + str(i + 1), value = str(len(message.guild.get_role(roleIds[i]).members)) + " Mitglieder", inline = True)

    data.set_author(name = "💭 Lerngruppen-Info")
    data.set_thumbnail(url = message.guild.icon_url)
    data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)    

async def templerngruppe(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl erstellt eine temporäre Lerngruppe für dich.
    !temlerngruppe
    """
    id = -1
    role_id = -1
    for i in range(len(message.author.roles)):
        if "templerngruppe" in message.author.roles[i].name:
            id = int(message.author.roles[i].name[14:], 16) 
            roleId = message.author.roles[i].id
            break    
    
    try:
        subcommand = message.content.split(" ")[1]
        if id == -1:
                await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du befindest dich in keiner temporären Lerngruppe!")
                return
            
        if subcommand == "add":
            mention_string = ""
            if len(message.mentions) == 0:
                await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Dieser Nutzer wurde nicht gefunden. Stelle sicher, dass der Name richtig geschrieben ist. Verwende `!command !templerngruppe` für weitere Hilfe!")      
                return
            for i in range(len(message.mentions)):
                mention_string = mention_string + " {0}".format(message.mentions[i])
                await message.mentions[i].add_roles(message.guild.get_role(roleId))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Die Mitglieder**{0}** wurden hinzugefügt!".format(mention_string))      
            return
            
        elif subcommand == "delete":
            all_channels = message.guild.channels
            for i in range(len(all_channels)):
                if str("templerngruppe" + hex(id)) in all_channels[i].name:
                    await all_channels[i].delete()
            await message.guild.get_role(roleId).delete()
            return
        
        elif subcommand == "null":
            pass
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!templerngruppe"))      
            return 
    except:
        pass
           
    if id != -1:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du befindest dich bereits in einer temporären Lerngruppe!")      
        return
            
    id = randint(0, 4095)
    newRole = await message.guild.create_role(name = "templerngruppe" + hex(id), color = discord.Colour(0xebd234), mentionable = True, reason = "Befehl von " + message.author.name + "#" + str(message.author.discriminator))
    overwrites = {
        message.guild.default_role: discord.PermissionOverwrite(read_messages = False),
        message.guild.get_role(newRole.id) : discord.PermissionOverwrite(   read_messages = True, 
                                                                            send_messages = True,
                                                                            manage_messages = True,                                                                           
                                                                            embed_links = True, 
                                                                            attach_files = True,
                                                                            read_message_history = True,
                                                                            external_emojis = True,
                                                                            connect = True,
                                                                            speak = True
                                                                        ),
    }
    newCategory = await message.guild.create_category(name = "templerngruppe" + hex(id), overwrites = overwrites, position = 26)
    newChannel = await message.guild.create_text_channel(name = "templerngruppe" + hex(id), category = newCategory)
    await message.guild.create_voice_channel(name = "templerngruppe" + hex(id), category = newCategory)
    await message.author.add_roles(newRole)
    await modules.bottiHelper._sendMessagePingAuthor(message, ":books: Es wurde eine temporäre Lerngruppe _(id : {0})_ erstellt!".format(hex(id)))
    await message.guild.get_channel(newChannel.id).send(":books: Dies ist eine temporäre Lerngruppe von {0}!\nVerwende `!templerngruppe add @USER`, um Mitglieder hinzuzufügen. Am besten nutzt du den `add`-Befehl in <#" + str(ids.channelIDs.bot_commands_ChannelID) + ">, da dort alle Nutzer gepingt werden können. `(@-Verwendung)`\nLöscht die temporäre Gruppe anschließend mit `!templerngruppe delete` !".format(message.author.mention))
