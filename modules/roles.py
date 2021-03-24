import discord
import modules.bottiHelper
import modules.data.ids as ids

def _changeRole(userRoles, removeIDs, addRole, guild):
    i = 0
    while(i < len(userRoles)):
        if userRoles[i].id in removeIDs:
            del userRoles[i]
            i = i - 1
            
        try:    
            if userRoles[i].id == addRole.id:
                return userRoles
        except AttributeError:
            pass
            
        i = i + 1
        
    if addRole != -1:
        userRoles.append(addRole)
        
    return userRoles

async def etit(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl verleiht dir die ETIT-Ersti-Rolle
    !etit
    """
    userRoles = message.author.roles
    addRole = message.guild.get_role(ids.roleIDs.ETIT_Ersti_RoleID)
    if addRole in userRoles:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du besitzt diese Rolle bereits!")
        return
    userRoles = _changeRole(userRoles, [ ids.roleIDs.MIT_Ersti_RoleID, ids.roleIDs.Paedagogik_RoleID, ids.roleIDs.Info_RoleID ], addRole, message.guild)
    
    await message.author.edit(roles = userRoles, reason="Requested by user.")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":white_check_mark: Dir wurde die ETIT-Ersti-Rolle verliehen!")   

async def matlab(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl verleiht dir die Matlab-Rolle
    !matlab
    """
    try:
        await message.author.add_roles(message.guild.get_role(ids.roleIDs.Matlab_RoleID), reason = "Requested by user.")
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du hast diese Rolle bereits!")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":white_check_mark: Dir wurde die Matlab-C++ Rolle verliehen!")

async def mit(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl verleiht dir die MIT-Ersti-Rolle
    !mit
    """
    userRoles = message.author.roles
    addRole = message.guild.get_role(ids.roleIDs.MIT_Ersti_RoleID)
    if addRole in userRoles:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du besitzt diese Rolle bereits!")
        return
    userRoles = _changeRole(userRoles, [ ids.roleIDs.ETIT_Ersti_RoleID, ids.roleIDs.Paedagogik_RoleID, ids.roleIDs.Info_RoleID ], addRole, message.guild)
    await message.author.edit(roles = userRoles, reason="Requested by user.")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":white_check_mark: Dir wurde die MIT-Ersti-Rolle verliehen!")
