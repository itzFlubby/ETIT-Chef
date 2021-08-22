import modules.gamble
import modules.guard
import modules.info
import modules.mod
import modules.data.ids     as ids

from __main__ import botti, slash
from modules.data.botData import botData

from discord_slash.context import ComponentContext, MenuContext
from discord_slash.model import ContextMenuType
from typing import Union

@slash.context_menu(target = ContextMenuType.USER,
                    name = "Userinfo",
                    guild_ids = [ids.serverIDs.ETIT_KIT])
async def Userinfo(ctx: MenuContext):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    msg = modules.construct._constructDummyMessage(ctx.author, ctx.channel, "")
    msg.mentions = [ ctx.target_author ]
    await ctx.send(content = "ContextMenu: Userinfo")
    await modules.info.userinfo(botti, msg, botData)
    
@slash.context_menu(target = ContextMenuType.USER,
                    name = "Kontostand",
                    guild_ids = [ids.serverIDs.ETIT_KIT])
async def Kontostand(ctx: MenuContext):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    msg = modules.construct._constructDummyMessage(ctx.author, ctx.channel, "")
    msg.mentions = [ ctx.target_author ]
    await ctx.send(content = "ContextMenu: Kontostand")
    await modules.gamble.balance(botti, msg, botData)
    
@slash.context_menu(target = ContextMenuType.MESSAGE,
                    name = "Purge until",
                    guild_ids = [ids.serverIDs.ETIT_KIT])
async def PurgeUntil(ctx: MenuContext):
    msg = modules.construct._constructDummyMessage(ctx.author, ctx.channel, "purge until {}".format(ctx.target_message.id))
    for module in botData.allCommandModules:
        if "purge" in module.commandNameList:
            if 0 not in module.allowedRoles:
                if not await modules.guard._checkPerms(botti, msg, module.allowedRoles, module.enableTrustet ):
                    return
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    
    await modules.mod.purge(botti, msg, botData)
    await ctx.send(content = "ContextMenu: Purge Until")