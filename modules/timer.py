import asyncio
import datetime
import discord
import modules.bottiHelper
import os

from random import randint

async def timer(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl startet einen Timer.
    !timer {DAUER}
    {DAUER} Ganze Zahl > 0, HH:MM:SS
    !timer 60\r!timer 01:00:00
    """
    try:
        timestring = message.content.split(" ")[1]
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "timer"))      
        return
        
    timeformat = timestring.count(":")
    seconds = 0
    minutes = 0
    hours = 0
    if timeformat == 0:
        if not timestring.isdigit():
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "timer"))      
            return
        seconds = int(timestring)
    elif timeformat == 1:
        minutesSeconds = timestring.split(":")
        if (not minutesSeconds[0].isdigit()) or (not minutesSeconds[1].isdigit()):
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "timer"))      
            return
        seconds = int(minutesSeconds[0]) * 60 + int(minutesSeconds[1])
    elif timeformat == 2:
        hoursMinutesSeconds = timestring.split(":")
        if (not hoursMinutesSeconds[0].isdigit()) or (not hoursMinutesSeconds[1].isdigit()) or (not hoursMinutesSeconds[2].isdigit()):
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "timer"))      
            return
        seconds = int(hoursMinutesSeconds[0]) * 3600 + int(hoursMinutesSeconds[1]) * 60 + int(hoursMinutesSeconds[2])
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "timer"))      
        return

    later = datetime.datetime.now() + datetime.timedelta(0, seconds)
    id = randint(0, 1024)
    botData.activeTimers.insert(len(botData.activeTimers) - 1, [hex(id)[2:], modules.bottiHelper._toSTRFTimestamp(later), botti.loop.create_task(timerNotify(botti, seconds, message, id))])
    
    data =  discord.Embed(
        title = "",
        color = 0x00ff00,
        description = ""
    )
    
    data.add_field(name = "Im Auftrag von", value = message.author.name + "#" + str(message.author.discriminator))
    data.add_field(name = "ID", value = hex(id)[2:])
    data.add_field(name = "Läuft ab in", value = str(seconds) + "s")
    
    data.set_author(name = "⏰ Timer")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Start: {0}\nEnde: {1}".format(modules.bottiHelper._getTimestamp(), modules.bottiHelper._toSTRFTimestamp(later)))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, content = ":alarm_clock: Dein Timer wurde registriert!", embed = data)

async def timercancel(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl stoppt einen Timer frühzeitig.
    !timercancel {ID}
    {ID} Timer-ID
    !timercancel ae3
    """
    try:
        timer = message.content.split(" ")[1]
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "timercancel"))      
        return
        
    for i in range(len(botData.activeTimers) - 1):
        iterTimer = botData.activeTimers[i]
        if iterTimer[0] == timer:
            iterTimer[2].cancel()
            await modules.bottiHelper._sendMessagePingAuthor(message, ":alarm_clock: Dein Timer auf **{}** _(ID: {})_ wurde frühzeitig beendet!".format(iterTimer[1], iterTimer[0]))
    
async def timerlist(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl listet alle aktiven Timer.
    !timerlist
    """
    for i in range(len(botData.activeTimers) - 1):
        if "finished" in str(botData.activeTimers[i][2]) or "cancelled" in str(botData.activeTimers[i][2]):
            del botData.activeTimers[i]
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":alarm_clock: Dies sind alle aktiven Timer:\n```\n{}```".format(str(botData.activeTimers).replace(os.getcwd()[:-10], "..").replace("], ", "],\n")))
     
async def timerNotify(botti, delay, message, id):
    await asyncio.sleep(delay)
    
    data =  discord.Embed(
        title = "",
        color = 0xff0000,
        description = ""
    )
    
    data.add_field(name = "Im Auftrag von", value = message.author.name + "#" + str(message.author.discriminator))
    data.add_field(name = "ID", value = hex(id)[2:])
    data.add_field(name = "Dauer", value = str(delay) + "s")
    
    data.set_author(name = "⏰ Timer")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, content = ":alarm_clock: Dein Timer ist abgelaufen!", embed = data)
