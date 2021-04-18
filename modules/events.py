import discord
import modules.bottiHelper
import modules.data.ids as ids
import modules.gamble
import modules.roles

from __main__ import botti

from modules.data.botData import botData

@botti.event
async def on_member_join(member):
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    channel = guild.get_channel(ids.channelIDs.NUTZER_UPDATES)
    
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
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    
    channel = guild.get_channel(ids.channelIDs.NUTZER_UPDATES)
    
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
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    
    if payload.channel_id in [ ids.channelIDs.AUSWAHL_ETIT_BSC, ids.channelIDs.AUSWAHL_MIT_BSC, ids.channelIDs.AUSWAHL_ETIT_MSC ]:
        if payload.emoji.name == "approve":
            member = guild.get_member(payload.user_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if len(message.role_mentions) != 0:
                await member.remove_roles(message.role_mentions[0], reason = "Requested by user.")    

@botti.event
async def on_raw_reaction_add(payload): 
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    
    # Vorschlag
    if payload.channel_id == ids.channelIDs.DM_ITZFLUBBY and payload.user_id == ids.userIDs.ITZFLUBBY:
        if botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel is None:
            await botti.get_user(ids.userIDs.ITZFLUBBY).create_dm()
        vorschlagMessage = (await botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel.fetch_message(payload.message_id)).content
        channel_BOT_TEST_LOBBY = guild.get_channel(ids.channelIDs.BOT_TEST_LOBBY)
        emojiToStatusname = { "✅": "angenommen", "💤": "on hold", "❌": "abgelehnt" }
        await channel_BOT_TEST_LOBBY.send(":bookmark_tabs: Statusänderung für Vorschlag von **{0}** ({1}) <@!{1}> `@{2}`\n`{3}`\nwurde auf {4} **{5}** gesetzt!".format(vorschlagMessage.split("**")[1], vorschlagMessage.split("(")[1][:18], vorschlagMessage.split("| ")[1], vorschlagMessage.split("'")[1], payload.emoji.name, emojiToStatusname[payload.emoji.name])) 
    
    # Personalisierung
    if payload.message_id == ids.messageIDs.REMOVE_ROLE_SELECT:
        emojiToRole = { "💬": ids.roleIDs.ZITATE, 
                        "🎼": ids.roleIDs.MUSIK, 
                        "👾": ids.roleIDs.MEMES,
                        "🎮": ids.roleIDs.GAMING,
                        "😺": ids.roleIDs.KATZEN,
                        "💻": ids.roleIDs.TECH_TALK,
                        "🎰": ids.roleIDs.SPIELHALLE,
                        "🐖": ids.roleIDs.VORLESUNGSSPAM }     
        if payload.emoji.name == "❌":     
            userRoles = modules.roles._changeRole(payload.member.roles, [ ids.roleIDs.ZITATE, ids.roleIDs.MUSIK, ids.roleIDs.MEMES, ids.roleIDs.GAMING, ids.roleIDs.KATZEN, ids.roleIDs.TECH_TALK, ids.roleIDs.SPIELHALLE, ids.roleIDs.VORLESUNGSSPAM, ids.roleIDs.FREIZEIT ], -1, guild)          
        else:
            userRoles = modules.roles._changeRole(payload.member.roles, [ emojiToRole[payload.emoji.name] ], -1, guild)
        await payload.member.edit(roles = userRoles, reason = "Requested by user.")  
        
    if payload.message_id == ids.messageIDs.MATLAB_SELECT:
        await payload.member.add_roles(guild.get_role(ids.roleIDs.MATLAB), reason = "Requested by user.")
      
    # Studiengangauswahl
    if payload.channel_id == ids.channelIDs.AUSWAHL_STUDIENGANG:
        emojiIDs = {    ids.emojiIDs.ETIT: 0, 
                        ids.emojiIDs.MIT: 1, 
                        ids.emojiIDs.KIT: 2, 
                        ids.emojiIDs.GAST: 3 }
        if payload.message_id == ids.messageIDs.AUSWAHL_BSC:
            roleSetupIDs = [ ids.roleIDs.ETIT_BSC_Einrichtung, ids.roleIDs.MIT_BSC_Einrichtung, ids.roleIDs.KIT_BSC_Einrichtung, ids.roleIDs.GAST ]
        elif payload.message_id == ids.messageIDs.AUSWAHL_MSC:
            roleSetupIDs = [ ids.roleIDs.ETIT_MSC_Einrichtung, ids.roleIDs.MIT_MSC_Einrichtung, ids.roleIDs.KIT_MSC_Einrichtung, ids.roleIDs.GAST ]
        else:
            return
            
        setupRole = guild.get_role(roleSetupIDs[emojiIDs[payload.emoji.id]])
        if setupRole not in payload.member.roles:
            await payload.member.add_roles(setupRole, reason = "Requested by user.")
            
    # Modulauswahl
    if payload.channel_id in [ ids.channelIDs.AUSWAHL_ETIT_BSC, ids.channelIDs.AUSWAHL_MIT_BSC, ids.channelIDs.AUSWAHL_ETIT_MSC, ids.channelIDs.AUSWAHL_MIT_MSC ]:
        if payload.emoji.name == "approve":
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            
            channelToRole = {   ids.channelIDs.AUSWAHL_ETIT_BSC: ids.roleIDs.ETIT_BSC, 
                                ids.channelIDs.AUSWAHL_MIT_BSC: ids.roleIDs.MIT_BSC, 
                                ids.channelIDs.AUSWAHL_ETIT_MSC: ids.roleIDs.ETIT_MSC,
                                ids.channelIDs.AUSWAHL_MIT_MSC: ids.roleIDs.MIT_MSC
                            }
            
            for setupRole in ids.roleIDs.setupRoles:
                if setupRole in [x.id for x in payload.member.roles]:
                    await payload.member.remove_roles(guild.get_role(setupRole), reason = "User set course.")
                    roles = payload.member.roles
                    for role_id in ids.roleIDs.newMemberJoinRoles:
                        if role_id not in [x.id for x in payload.member.roles]:
                            roles.append(guild.get_role(role_id))
                    
                    if setupRole in [ ids.roleIDs.KIT_BSC_Einrichtung, ids.roleIDs.KIT_MSC_Einrichtung ]:
                        setupRoleToNormalRole = {   ids.roleIDs.KIT_BSC_Einrichtung: ids.roleIDs.KIT_BSC,
                                                    ids.roleIDs.KIT_MSC_Einrichtung: ids.roleIDs.KIT_MSC
                                                }   
                        roles.append(guild.get_role(setupRoleToNormalRole[setupRole]))
                    else:
                        if channelToRole[payload.channel_id] not in [x.id for x in payload.member.roles]:
                            roles.append(guild.get_role(channelToRole[payload.channel_id]))
                    
                    await payload.member.edit(roles = roles, reason = "User set course.")
                    break
              
            if len(message.role_mentions) == 0:
                channel_sdadisdigen = guild.get_channel(ids.channelIDs.SDADISDIGEN)
                await channel_sdadisdigen.send("👤 {} hat in <#{}> **{}** ausgewählt <@!{}>".format(payload.member.mention, payload.channel_id, message.content, ids.userIDs.DAVID))
                return
              
            role = message.role_mentions[0]
            if role not in payload.member.roles:
                await payload.member.add_roles(role, reason = "Requested by user.")
   
    # DANKE               
    if payload.emoji.id == ids.emojiIDs.DANKE:
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
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    
    channel = guild.get_channel(ids.channelIDs.DEV_INTERNAL)
    
    onlineIconDict = {
        discord.Status.online: "<:online:" + str(ids.emojiIDs.ONLINE) + ">",
        discord.Status.offline: "<:offline:" + str(ids.emojiIDs.OFFLINE) + ">",
        discord.Status.idle: "<:idle:" + str(ids.emojiIDs.IDLE) + ">",
        discord.Status.dnd: "<:dnd:" + str(ids.emojiIDs.DND) + ">"
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
    
    if after.id == ids.userIDs.ETIT_MASTER:
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
            await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.BOT_TEST_LOBBY).send(content = "<@192701441188560900>", embed = data)
"""