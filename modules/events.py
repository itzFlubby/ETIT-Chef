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
    
    channel = guild.get_channel(ids.channelIDs.allgemein_ChannelID)
    
    data = discord.Embed(
        title = member.name + "#" + str(member.discriminator),
        color = 0x00FF00,
        description = "ist dem Server beigetreten!"
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
    
    channel = guild.get_channel(ids.channelIDs.allgemein_ChannelID)
    
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
             updatedStatus = "on hold"
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