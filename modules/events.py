import discord
import modules.bottiHelper
import modules.data.ids as ids
import modules.gamble
import modules.roles

from __main__ import botti

from modules.data.botData import botData

@botti.event
async def on_member_join(member):
    roles = []
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    for role_id in ids.roleIDs.newMemberJoinRoles:
        roles.append(guild.get_role(role_id))
    await member.edit(roles = roles, reason = "Mitglieder beitritt.")
    
    channel = guild.get_channel(ids.channelIDs.nutzer_updates_ChannelID)
    
    data = discord.Embed(
        title = member.name + "#" + str(member.discriminator),
        color = 0x00FF00,
        description = "<@!" + str(member.id) + "> ist dem Server beigetreten!"
    )
    data.add_field(name = "Server beigetreten am", value = modules.bottiHelper._toGermanTimestamp(member.joined_at), inline = False)
    data.add_field(name = "Account erstellt am", value = modules.bottiHelper._toGermanTimestamp(member.created_at), inline = False)
    

    data.set_author(name = "💎 Mitglieder-Beitritt")
    data.set_thumbnail(url = member.avatar_url)
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
    
    await channel.send(embed = data)
    
@botti.event
async def on_member_remove(member):
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    
    channel = guild.get_channel(ids.channelIDs.nutzer_updates_ChannelID)
    
    data = discord.Embed(
        title = member.name + "#" + str(member.discriminator),
        color = 0xFF0000,
        description = "hat den Server verlassen!"
    )
    data.add_field(name = "Server beigetreten am", value = modules.bottiHelper._toGermanTimestamp(member.joined_at), inline = False)
    data.add_field(name = "Account erstellt am", value = modules.bottiHelper._toGermanTimestamp(member.created_at), inline = False)
    

    data.set_author(name = "😭 Mitglieder-Austritt")
    data.set_thumbnail(url = member.avatar_url)
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
    
    await channel.send(embed = data)

@botti.event
async def on_raw_reaction_remove(payload):
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    
    if payload.channel_id in [ ids.channelIDs.auswahl_BSC_ETIT_ChannelID, ids.channelIDs.auswahl_BSC_MIT_ChannelID, ids.channelIDs.auswahl_MSC_ETIT_ChannelID ]:
        if payload.emoji.name == "approve":
            member = guild.get_member(payload.user_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if len(message.role_mentions) != 0:
                await member.remove_roles(message.role_mentions[0], reason = "Requested by user.")    

@botti.event
async def on_raw_reaction_add(payload): 
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    
    # Vorschlag
    if payload.channel_id == ids.channelIDs.dm_itzFlubby_ChannelID and payload.user_id == ids.userIDs.itzFlubby_ID:
        if botti.get_user(ids.userIDs.itzFlubby_ID).dm_channel is None:
            await botti.get_user(ids.userIDs.itzFlubby_ID).create_dm()
        vorschlagMessage = (await botti.get_user(ids.userIDs.itzFlubby_ID).dm_channel.fetch_message(payload.message_id)).content
        channel_botTestLobby_ChannelID = guild.get_channel(ids.channelIDs.botTestLobby_ChannelID)
        emojiToStatusname = { "✅": "angenommen", "💤": "on hold", "❌": "abgelehnt" }
        await channel_botTestLobby_ChannelID.send(":bookmark_tabs: Statusänderung für Vorschlag von **{0}** ({1}) <@!{1}> `@{2}`\n`{3}`\nwurde auf {4} **{5}** gesetzt!".format(vorschlagMessage.split("**")[1], vorschlagMessage.split("(")[1][:18], vorschlagMessage.split("| ")[1], vorschlagMessage.split("'")[1], payload.emoji.name, emojiToStatusname[payload.emoji.name])) 
    
    # Personalisierung
    if payload.message_id == ids.messageIDs.removeRoleSelect_MessageID:
        emojiToRole = { "💬": ids.roleIDs.Zitate_RoleID, 
                        "🎼": ids.roleIDs.Musik_RoleID, 
                        "👾": ids.roleIDs.Memes_RoleID,
                        "🎮": ids.roleIDs.Gaming_RoleID,
                        "😺": ids.roleIDs.Katzen_RoleID,
                        "💻": ids.roleIDs.tech_talk_RoleID,
                        "🎰": ids.roleIDs.Spielhalle_RoleID,
                        "🐖": ids.roleIDs.Vorlesungsspam_RoleID }     
        if payload.emoji.name == "❌":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.Zitate_RoleID, ids.roleIDs.Musik_RoleID, ids.roleIDs.Memes_RoleID, ids.roleIDs.Gaming_RoleID, ids.roleIDs.Katzen_RoleID, ids.roleIDs.tech_talk_RoleID, ids.roleIDs.Spielhalle_RoleID, ids.roleIDs.Vorlesungsspam_RoleID, ids.roleIDs.Freizeit_RoleID ], -1, guild)          
        else:
            userRoles = modules.roles._changeRole(payload.member.roles, [ emojiToRole[payload.emoji.name] ], -1, guild)
        await payload.member.edit(roles = userRoles, reason = "Requested by user.")  
        
    if payload.message_id == ids.messageIDs.matlabSelect_MessageID:
        await payload.member.add_roles(guild.get_role(ids.roleIDs.Matlab_RoleID), reason = "Requested by user.")
        
    # Modulauswahl
    if payload.channel_id in [ ids.channelIDs.auswahl_BSC_ETIT_ChannelID, ids.channelIDs.auswahl_BSC_MIT_ChannelID, ids.channelIDs.auswahl_MSC_ETIT_ChannelID ]:
        if payload.emoji.name == "approve":
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if len(message.role_mentions) == 0:
                channel_dev_internal_ChannelID = guild.get_channel(ids.channelIDs.devInternal_ChannelID)
                await channel_dev_internal_ChannelID.send("👤 {} hat in <#{}> **{}** ausgewählt <@!{}>".format(payload.member.mention, payload.channel_id, message.content, ids.userIDs.David_ID))
                return
            role = message.role_mentions[0]
            if role not in payload.member.roles:
                await payload.member.add_roles(role, reason = "Requested by user.")
   
    # DANKE               
    if payload.emoji.id == ids.emojiIDs.danke_EmojiID:
        channel = payload.member.guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.user_id == message.author.id:
            await message.add_reaction("❌")
            return
        for reaction in message.reactions:
            if reaction.me == True:
                return
        if modules.gamble._getBalance(botData, message.author.id) == -1:
            modules.gamble._createAccount(botData, message.author.id)
        modules.gamble._addBalance(botData, message.author.id, 1500)
        await message.add_reaction("✅")
"""        
@botti.event
async def on_member_update(before, after):
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT_ServerID)
    
    channel = guild.get_channel(ids.channelIDs.devInternal_ChannelID)
    
    onlineIconDict = {
        discord.Status.online: "<:online:" + str(ids.emojiIDs.online_EmojiID) + ">",
        discord.Status.offline: "<:offline:" + str(ids.emojiIDs.offline_EmojiID) + ">",
        discord.Status.idle: "<:idle:" + str(ids.emojiIDs.idle_EmojiID) + ">",
        discord.Status.dnd: "<:dnd:" + str(ids.emojiIDs.dnd_EmojiID) + ">"
    }
    
    data = discord.Embed(
        title = after.name + "#" + str(after.discriminator),
        color = 0x0066FF,
        description = "<@" + str(after.id) + "> wurde aktualisiert!"
    )
    
    data.add_field(name = "Status", value = "{} {} -> {} {}".format(str(before.status), str(onlineIconDict[before.status]), str(after.status), str(onlineIconDict[after.status])), inline = False)
    data.add_field(name = "Aktivität", value = str(before.activity) + " -> " + str(after.activity), inline = False)

    data.set_author(name = "🔃 Mitglieder-Aktualisierung")
    data.set_thumbnail(url = after.avatar_url)
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
    
    await channel.send(embed = data)
    
    if after.id == ids.userIDs.ETIT_Master_ID:
        if after.status == discord.Status.offline:
            data = discord.Embed(
                title = "",
                description = "",
                color = 0xFF0000
            )
            data.add_field(name = "HEY CHRISTOPH", value = "Da StImMt WaS nIcHt. RePaRiErE dAs!1!!elf!!")
            data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
            data.set_thumbnail(url = botti.user.avatar_url)
            data.set_author(name = "📡 Offline-Detektor")
            await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.botTestLobby_ChannelID).send(content = "<@192701441188560900>", embed = data)
"""