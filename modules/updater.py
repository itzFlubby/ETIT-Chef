import asyncio
import datetime
import discord
import modules.bottiHelper
import modules.calendar
import modules.construct
import modules.data.ids as ids
import requests

from __main__ import botti
from modules.data.botData import botData

async def _cyclicUpdater():
    channelBTL = discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.BOT_TEST_LOBBY)
    
    while(True):
        await asyncio.sleep(3600 * 12) # every 12 hours
        updatedCalendars = "```\n"
        for calendar in botData.calendarURLs.keys():
            print(calendar)
            if botData.calendarURLs[calendar] != None:
                
                request = requests.get(botData.calendarURLs[calendar])
                with open(botData.modulesDirectory + "data/calendar/" + calendar + ".ical", "w+") as f:
                    f.write(request.text.replace("\r", ""))
                    
                modules.calendar._retrieveExams(botData, calendar)
                
                modules.calendar._updateAll(botData)
                modules.calendar._retrieveExams(botData, "all")
                
                updatedCalendars += calendar + "\n"
                
        embed = modules.construct._constructDefaultEmbed(
            title = "",
            description = "",
            color = 0x009aff,
            author = {
                "name": "🔄 Zyklisches Update"
            }
        )
        
        embed.add_field(name = "Aktualisierte Kalender", value = updatedCalendars + "```")
        
        await channelBTL.send(embed = embed)
        