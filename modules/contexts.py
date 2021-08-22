import modules.info
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