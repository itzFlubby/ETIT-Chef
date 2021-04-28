import discord
import modules.bottiHelper
import modules.data.ids as ids

emojiToRoleID = {   "💬": ids.roleIDs.ZITATE, 
                    "🎼": ids.roleIDs.MUSIK, 
                    "👾": ids.roleIDs.MEMES,
                    "🎮": ids.roleIDs.GAMING,
                    "😺": ids.roleIDs.KATZEN,
                    "💻": ids.roleIDs.TECH_TALK,
                    "🎰": ids.roleIDs.SPIELHALLE,
                    "🐖": ids.roleIDs.VORLESUNGSSPAM,
                    "⚽": ids.roleIDs.SPORT,
                    "🚀": ids.roleIDs.STONKS
                }        

async def _addRoles(member, addIDs):
    memberRoles = member.roles
    for roleID in addIDs:
        role = member.guild.get_role(roleID)
        if not (role in memberRoles):
            memberRoles.append(role)
            
    await member.edit(roles = memberRoles) 
    
async def _removeRoles(member, removeIDs):
    memberRoles = member.roles
    for roleID in removeIDs:
        role = member.guild.get_role(roleID)
        if (role in memberRoles):
            memberRoles.remove(role)
            
    await member.edit(roles = memberRoles)
    
           