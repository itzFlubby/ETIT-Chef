import discord
import modules.bottiHelper
import modules.data.ids as ids
import modules.gamble
import modules.lerngruppe
import modules.roles

from __main__ import botti

from modules.data.botData import botData

@botti.event
async def on_interaction(interaction):
    message = interaction.message
    data = interaction.data
    if message != None:
        if message.embeds != None:
            embed = message.embeds[0]
            if ":question: Befehls-Hilfe" == embed.title:
                await modules.utils._updateHelpEmbed(message, int(data["custom_id"]), botData.allCommandModules, botData)
                
            if "Abstimmung" == embed.title:
                await modules.polls._updatePoll(message, data["custom_id"], interaction.user, botData)

@botti.event
async def on_member_join(member):
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    channel = guild.get_channel(ids.channelIDs.NUTZER_UPDATES)
    
    data = discord.Embed(
        title = member.name + "#" + str(member.discriminator),
        color = 0x00FF00,
        description = "<@" + str(member.id) + "> ist dem Server beigetreten!"
    )
    data.add_field(name = "Server beigetreten am", value = modules.bottiHelper._toUTCTimestamp(member.joined_at), inline = False)
    data.add_field(name = "Account erstellt am", value = modules.bottiHelper._toUTCTimestamp(member.created_at), inline = False)

    data.set_author(name = "💎 Mitglieder-Beitritt")
    data.set_thumbnail(url = member.avatar.url)
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
    data.add_field(name = "Server beigetreten am", value = modules.bottiHelper._toUTCTimestamp(member.joined_at), inline = False)
    data.add_field(name = "Account erstellt am", value = modules.bottiHelper._toUTCTimestamp(member.created_at), inline = False)
    

    data.set_author(name = "😭 Mitglieder-Austritt")
    data.set_thumbnail(url = member.avatar.url)
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
    
    botMessage = await channel.send(embed = data)
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.PAYRESPECT))
    
@botti.event
async def on_raw_reaction_remove(payload):
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    member = guild.get_member(payload.user_id)
    
    if payload.channel_id in [ ids.channelIDs.AUSWAHL_ETIT_BSC, ids.channelIDs.AUSWAHL_MIT_BSC, ids.channelIDs.AUSWAHL_ETIT_MSC ]:
        if payload.emoji.name == "approve":
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if len(message.role_mentions) != 0:
                await member.remove_roles(message.role_mentions[0], reason = "Requested by user.")

    if payload.message_id == ids.messageIDs.REMOVE_ROLE_SELECT:
        await modules.roles._addRoles(member, [ modules.roles.emojiToRoleID[payload.emoji.name] ])
                
@botti.event
async def on_raw_reaction_add(payload): 
    guild = botti.get_guild(ids.serverIDs.ETIT_KIT)
    
    # Vorschlag
    if payload.channel_id == ids.channelIDs.DM_ITZFLUBBY and payload.user_id == ids.userIDs.ITZFLUBBY:
        devDM = await modules.bottiHelper._createDM(botti, ids.userIDs.ITZFLUBBY)
        vorschlagMessage = (await devDM.fetch_message(payload.message_id)).content
        userDM = await modules.bottiHelper._createDM(botti, int(vorschlagMessage.split("(")[1][:18]))
        channel_BTL = guild.get_channel(ids.channelIDs.BOT_TEST_LOBBY)
        emojiToStatusname = {   "✅": "angenommen", 
                                "💤": "on hold", 
                                "❌": "abgelehnt",
                                "👑": "erledigt"
                            }
        await userDM.send(":bookmark_tabs: Statusänderung für Vorschlag von **{0}** ({1}) <@!{1}> `@{2}`\n`{3}`\nwurde auf {4} **{5}** gesetzt!".format(vorschlagMessage.split("**")[1], vorschlagMessage.split("(")[1][:18], vorschlagMessage.split("| ")[1], vorschlagMessage.split("'")[1], payload.emoji.name, emojiToStatusname[payload.emoji.name])) 
        await channel_BTL.send(":bookmark_tabs: Statusänderung für Vorschlag von **{0}** ({1}) <@!{1}> `@{2}`\n`{3}`\nwurde auf {4} **{5}** gesetzt!".format(vorschlagMessage.split("**")[1], vorschlagMessage.split("(")[1][:18], vorschlagMessage.split("| ")[1], vorschlagMessage.split("'")[1], payload.emoji.name, emojiToStatusname[payload.emoji.name])) 
    
    # Personalisierung
    if payload.message_id == ids.messageIDs.REMOVE_ROLE_SELECT: 
        await modules.roles._removeRoles(payload.member, [ modules.roles.emojiToRoleID[payload.emoji.name] ])
        
    if payload.message_id == ids.messageIDs.MATLAB_SELECT:
        await payload.member.add_roles(guild.get_role(ids.roleIDs.MATLAB), reason = "Requested by user.")
      
    # Studiengangauswahl
    if payload.channel_id == ids.channelIDs.AUSWAHL_STUDIENGANG:
        emojiIDs = {    ids.emojiIDs.ETIT["id"]: 0, 
                        ids.emojiIDs.MIT["id"]: 1, 
                        ids.emojiIDs.KIT["id"]: 2, 
                        ids.emojiIDs.GAST["id"]: 3 }
        if payload.message_id == ids.messageIDs.AUSWAHL_BSC:
            roleSetupIDs = [ ids.roleIDs.ETIT_BSC_Einrichtung, ids.roleIDs.MIT_BSC_Einrichtung, ids.roleIDs.KIT_BSC_Einrichtung, ids.roleIDs.GAST ]
        elif payload.message_id == ids.messageIDs.AUSWAHL_MSC:
            roleSetupIDs = [ ids.roleIDs.ETIT_MSC_Einrichtung, ids.roleIDs.MIT_MSC_Einrichtung, ids.roleIDs.KIT_MSC_Einrichtung, ids.roleIDs.GAST ]
        else:
            return
            
        userRoles = payload.member.roles
        userRoleIDs = [role.id for role in userRoles]    
        setupRole = guild.get_role(roleSetupIDs[emojiIDs[payload.emoji.id]])
        if setupRole not in payload.member.roles:
            userRoles.append(setupRole)
            if setupRole.id == ids.roleIDs.GAST: # Add roles to guest, as guest doesn't see #modulauswahl
                for roleID in ids.roleIDs.newMemberJoinRoles:
                    if roleID not in userRoleIDs:
                        userRoles.append(guild.get_role(roleID))
            await payload.member.edit(roles = userRoles, reason = "User selected Group.")
                
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
            
            userRoles = payload.member.roles
            userRoleIDs = [role.id for role in userRoles]
            setupRoleIDs = [roleID for roleID in ids.roleIDs.setupRoles if roleID in userRoleIDs]
            if bool(setupRoleIDs): # If user has a setup role
                setupRoleID = setupRoleIDs[0] # Take first element, because this list WILL only have one element. EVER.
                setupRole = guild.get_role(setupRoleID)
                
                userRoles.remove(setupRole)
                    
                for roleID in ids.roleIDs.newMemberJoinRoles:
                    if roleID not in userRoleIDs:
                        userRoles.append(guild.get_role(roleID))
                    
                if setupRoleID in [ ids.roleIDs.KIT_BSC_Einrichtung, ids.roleIDs.KIT_MSC_Einrichtung ]:
                    setupRoleToNormalRole = {   ids.roleIDs.KIT_BSC_Einrichtung: ids.roleIDs.KIT_BSC,
                                                ids.roleIDs.KIT_MSC_Einrichtung: ids.roleIDs.KIT_MSC
                                            }   
                    userRoles.append(guild.get_role(setupRoleToNormalRole[setupRoleID]))
                else:
                    if channelToRole[payload.channel_id] not in userRoleIDs:
                        userRoles.append(guild.get_role(channelToRole[payload.channel_id]))
                
                await payload.member.edit(roles = userRoles, reason = "User set course.")

              
            if len(message.role_mentions) == 0:
                channel_sdadisdigen = guild.get_channel(ids.channelIDs.SDADISDIGEN)
                await channel_sdadisdigen.send("👤 {} hat in <#{}> **{}** ausgewählt <@!{}>".format(payload.member.mention, payload.channel_id, message.content, ids.userIDs.DAVID))
            else:                  
                role = message.role_mentions[0]
                if role not in payload.member.roles:
                    await payload.member.add_roles(role, reason = "Requested by user.")
   
    # LERNGRUPPE
    if payload.emoji.name == "approve":
        if payload.member.id == botti.user.id:
            return
        
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if (message.author.id == botti.user.id) and ("lerngruppe-" in message.content.lower()):
            id = int(message.content.split("-")[1].split("**:")[0])
            
            dummyMessage = modules.construct._constructDummyMessage(payload.member, guild.get_channel(payload.channel_id), "{prefix}lerngruppe join {id}".format(prefix = botData.botPrefix, id = id))
            await modules.lerngruppe._subcommandJoin(dummyMessage, dummyMessage.content.split(" "), botData)
   
    # DANKE
    if payload.emoji.id == ids.emojiIDs.DANKE["id"]:
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
