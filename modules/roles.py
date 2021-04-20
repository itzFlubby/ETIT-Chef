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