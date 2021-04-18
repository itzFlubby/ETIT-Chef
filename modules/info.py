import datetime
import discord
import modules.bottiHelper
import modules.data.ids as ids
import os
import platform
import psutil

from icalendar import Calendar, vDatetime
from mcstatus import MinecraftServer

async def botinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Botinfo an.
    !botinfo
    """
    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = ""
    )
    data.add_field(name = "Präfix", value = "!")
    data.add_field(name = "Name", value = botti.user.name)
    data.add_field(name = "Discriminator", value = str(("#" + botti.user.discriminator)))
    
    data.add_field(name = "Sprache", value = "Deutsch")
    data.add_field(name = "Vertretene Server" , value = str(len(botti.guilds)))
    data.add_field(name = "OS", value = platform.system() + "-" + str(os.name).upper() + "-" + platform.release())
    
    data.add_field(name = "Discord API Version", value = discord.__version__)
    data.add_field(name = "Latenz", value = str(round((botti.latency * 1000), 2)) + "ms")
    data.add_field(name = "Entwickler", value = "itzFlubby")
    
    data.add_field(name = "GitHub", value = "https://github.com/itzFlubby/ETIT-Chef/", inline = False)
    
    data.set_author(name = "🤖 Bot-Info")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "ID: {0}\nBei Verbesserungsvorschlägen: !vorschlag <NACHRICHT>\nStand: {1}".format(str(botti.user.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def channelinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Kanal-Info an.
    !channelinfo {@KANAL}
    {@KANAL} "", Kanal-Erwähnung
    !channelinfo\r!channelinfo #allgemein
    """
    channelToGetInfo = message.channel
    if len(message.channel_mentions) != 0:
        channelToGetInfo = message.channel_mentions[0]

    data =  discord.Embed(
        title = "",
        color = 0x005dff,
        description = ""
    )
    data.add_field(name = "Name", value = channelToGetInfo.name)
    data.add_field(name = "Typ", value = channelToGetInfo.type)
    data.add_field(name = "Position", value = str(channelToGetInfo.position + 1))
    
    data.add_field(name = "Erstellt am", value = modules.bottiHelper._toGermanTimestamp(channelToGetInfo.created_at))
    data.add_field(name = "Slow-Modus", value = str(channelToGetInfo.slowmode_delay) + "s") 
    data.add_field(name = "Mitglieder", value = str(len(channelToGetInfo.members))) 
    
    data.add_field(name = "NSFW", value = channelToGetInfo.is_nsfw()) 
    data.add_field(name = "NEWS", value = channelToGetInfo.is_news()) 
    data.add_field(name = "Kategorie-ID", value = str(channelToGetInfo.category_id)) 
    
    data.add_field(name = "Thema", value = channelToGetInfo.topic, inline = False)
    
    data.set_author(name = "💬 Kanal-Info")
    data.set_thumbnail(url = message.guild.icon_url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(channelToGetInfo.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def minecraft(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Minecraft-Server-Info an.
    !minecraft
    """    
    data = discord.Embed(
        title = "{emoji} Server-Status".format(emoji = modules.bottiHelper._constructEmojiString(ids.emojiIDs.MINECRAFT)),
        color = 0x00ff00,
        description = botData.minecraftServerName
    )
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
    
    try:
        server = MinecraftServer.lookup(botData.minecraftServerName)
        
        status = server.status()
        query = server.query()
        
        data.add_field(name = "Latenz", value = str(status.latency) + "ms", inline = False)
        data.add_field(name = "Version", value = "{0} {1}\n[Modded] Direwolf20 v2.5.0".format(query.software.brand, query.software.version))
        data.add_field(name = "Spieler", value = "**{0} / {1}**".format(status.players.online, status.players.max) + ("\n```\n{0}```".format(",\n".join(query.players.names)) if status.players.online != 0 else ""), inline = False)
    except:
        data.color = 0xff0000
        data.add_field(name = "Offline", value = "Der Server ist nicht erreichbar.")
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)
    
async def permissions(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Berechtigungen für einen Nutzer an.
    !permissions {@USER}
    {@USER} "", Nutzer-Erwähnung
    !permissions\r!permissions @ETIT-Chef
    """
    isUser = True
    if len(message.role_mentions) != 0:
        isUser = False
        role = message.role_mentions[0]
        perm_list = list(role.permissions)
    
    if isUser:
        user = message.author
    
        if len(message.mentions) != 0:
            user = message.mentions[0]

        perm_list = list(user.permissions_in(message.channel))
    
    perm_list = str(perm_list).split("[(")[1]
    perm_list = perm_list.split(")]")[0]
    total_string = ""

    cuttedStrings = perm_list.split("), (")
    for i in range(len(cuttedStrings)):
        if isUser and (cuttedStrings[i] in [ "'priority_speaker', False", "'stream', False", "'connect', False", "'speak', False", "'mute_members', False", "'deafen_members', False", "'move_members', False", "'use_voice_activation', False" ]):
            continue
        total_string = total_string + cuttedStrings[i] + "\n"

    total_string = total_string.replace(", True", " {emoji} (True)".format(emoji = modules.bottiHelper._constructEmojiString(ids.emojiIDs.APPROVE)))
    total_string = total_string.replace(", False", " {emoji} (False)".format(emoji = modules.bottiHelper._constructEmojiString(ids.emojiIDs.DENY)))
    total_string = total_string.replace("'", "`")
    if isUser:
        await modules.bottiHelper._sendMessage(message, ":shield: Dies sind die Berechtigungen für **{0}** _in {1}_ {2}:\n{3}".format(user.mention, message.channel.name, message.author.mention, total_string))
    else:    
        await modules.bottiHelper._sendMessage(message, ":shield: Dies sind die globalen Berechtigungen für **{0}** _wenn nicht anderweitig gesetzt_:\n{1}".format(role.mention, total_string))

async def ping(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die WebSocket-Protokoll-Latenz an.
    !ping
    """
    await modules.bottiHelper._sendMessagePingAuthor(message, ":satellite: Die Discord WebSocket-Protokoll-Latenz liegt bei **{0}ms**!".format(str(round((botti.latency * 1000), 2)))) 

async def roleinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Rollen-Info an.
    !roleinfo {@ROLLE}
    {@ROLLE} "", Rollen-Erwähnung
    !roleinfo\r!roleinfo @Bot
    """
    try:
        role = message.role_mentions[0]
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "roleinfo"))      
        return
    data = discord.Embed(
        title = "",
        color = role.color.value,
        description = ""
    )
    data.add_field(name = "Name", value = role.name)
    data.add_field(name = "Position", value = str(role.position))
    data.add_field(name = "Gruppiert", value = str(role.hoist))
    
    data.add_field(name = "Rolle erstellt am", value = modules.bottiHelper._toGermanTimestamp(role.created_at))
    data.add_field(name = "Farbe", value = hex(role.color.value))
    data.add_field(name = "Mitglieder", value = len(role.members))
    
    data.add_field(name = "Erwähnbar", value = str(role.mentionable))
    data.add_field(name = "Standard", value = str(role.is_default()))
    
    data.set_author(name = "🧾 Rollen-Info")
    data.set_thumbnail(url = message.guild.icon_url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(role.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def serverinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Server-Info an.
    !serverinfo
    """
    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = ""
    )
    
    data.add_field(name = "Name", value = message.guild.name)
    data.add_field(name = "Region", value = str(message.guild.region))
    data.add_field(name = "Eigentümer", value = message.guild.owner.name + "#" + str(message.guild.owner.discriminator))
    
    data.add_field(name = "User", value = message.guild.member_count)
    data.add_field(name = "Rollen", value = len(message.guild.roles))
    data.add_field(name = "Emojis", value = len(message.guild.emojis))
    
    data.add_field(name = "Text Channels", value = len(message.guild.text_channels))
    data.add_field(name = "Sprach Channels", value = len(message.guild.voice_channels))
    data.add_field(name = "Erstellt am", value = modules.bottiHelper._toGermanTimestamp(message.guild.created_at))
    
    data.add_field(name = "Icon", value = message.guild.icon_url, inline = False)
    
    data.set_author(name = "📱 Server-Info")
    data.set_thumbnail(url = message.guild.icon_url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(message.guild.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def stats(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Bot-Statistiken an.
    !stats
    """
    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = ""
    )
    
    data.add_field(name = "OS", value = platform.system() + "-" + str(os.name).upper() + "-" + platform.release())
    data.add_field(name = "Prozessor", value = platform.machine())
    data.add_field(name = "Prozessor-Kerne", value = psutil.cpu_count())
    
    process = psutil.Process(os.getpid())
    data.add_field(name = "CPU", value = str(round(process.cpu_percent(), 2)) + "%")
    data.add_field(name = "CPU-Zeit", value = str(round(sum(process.cpu_times()), 2)) + "s")
    data.add_field(name = "Läuft auf Kern", value = str(process.cpu_num()))
    
    data.add_field(name = "RAM", value = str(round(process.memory_percent(), 2)) + "%")
    data.add_field(name = "RSS", value = str(process.memory_info()[0]))
    data.add_field(name = "VMS", value = str(process.memory_info()[1]))
    
    data.add_field(name = "IO Read", value = str(process.io_counters()[4]))
    data.add_field(name = "IO Write", value = str(process.io_counters()[3]))
    data.add_field(name = "Status", value = str(process.status()))
    
    
    
    data.add_field(name = "Python Version", value = platform.python_version())
    data.add_field(name = "Python Build", value = str(platform.python_build()).replace("'", "").replace("(", "").replace(")", ""))
    data.add_field(name = "PID", value = os.getpid())
    
    
    
    if os.name == "nt":
        data.set_thumbnail(url = "https://www.seeklogo.net/wp-content/uploads/2012/12/windows-8-icon-logo-vector-400x400.png")
    elif os.name == "posix":
        data.set_thumbnail(url = "https://www.raspberrypi.org/app/uploads/2011/10/Raspi-PGB001.png")
    else:
        data.set_thumbnail(url = botti.user.avatar_url)
    
    data.set_author(name = "📑 Stats")
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
  
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def test(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl überprüft, ob der Bot online ist.
    !test
    """
    botMessage = await modules.bottiHelper._sendMessagePingAuthor(message, ":globe_with_meridians: Der Bot ist online und läuft ordnungsgemäß!")
    await botMessage.add_reaction(modules.bottiHelper._constructEmojiStringNoBracket(ids.emojiIDs.NEIN))
    await botMessage.add_reaction(modules.bottiHelper._constructEmojiStringNoBracket(ids.emojiIDs.DOCH))
    await botMessage.add_reaction(modules.bottiHelper._constructEmojiStringNoBracket(ids.emojiIDs.OH))

async def uptime(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt an, wie langer der Bot schon online ist.
    !uptime
    """
    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = ""
    )
    
    difference = datetime.datetime.now() - botData.startTimestamp
    hours = (difference.seconds // 3600) % 24
    minutes = (difference.seconds // 60) % 60
    seconds = difference.seconds % 60
    data.add_field(name = "Zeit seit letztem Neustart", value = "{0} Tage, {1} Stunden, {2} Minuten, {3} Sekunden".format(str(difference.days), hours, minutes, seconds))
    
    data.set_author(name = "⏱ Uptime")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Seitdem wurden {0} Befehle ausgeführt!\nStand: {1}".format(botData.befehlsCounter, modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def userinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Info über einen Nutzer an.
    !userinfo {@USER}
    {@USER} "", Nutzer-Erwähnung
    !userinfo\r!userinfo @ETIT-Chef
    """
    user = message.author
    if len(message.mentions) != 0:
        user = message.mentions[0]

    data = discord.Embed(
        title = "",
        color = user.top_role.color.value,
        description = ""
    )
    
    data.add_field(name = "Name", value = user.name)
    data.add_field(name = "Discriminator", value = "#{0}".format(user.discriminator))
    data.add_field(name = "Nick", value = user.nick)
    
    data.add_field(name = "Bot-User", value = user.bot)
    data.add_field(name = "Höchste Rolle", value = user.top_role)
    
    data.add_field(name = "Server beigetreten am", value = modules.bottiHelper._toGermanTimestamp(user.joined_at))
    data.add_field(name = "Account erstellt am", value = modules.bottiHelper._toGermanTimestamp(user.created_at))
    
    data.add_field(name = "Profilbild", value = user.avatar_url, inline = False)
    
    data.set_author(name = "👨‍🎓 User-Info")
    data.set_thumbnail(url = user.avatar_url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(user.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

async def voiceinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Sprach-Info an.
    !voiceinfo
    """
    voiceClients = botti.voice_clients
    if not voiceClients:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Bot befindet sich in keinem Sprach-Kanal. Nutze **'!connect'**, um den Bot zu einem Sprach-Kanal zu verbinden.")
        return

    for x in range(len(voiceClients)):
        if message.guild.name is voiceClients[x].guild.name:
            voiceClient = voiceClients[x]
    
    data = discord.Embed(
        title = "",
        color = 0xb43cf0,
        description = ""
    )
    
    data.add_field(name = "Kanal", value = voiceClient.channel.name)
    data.add_field(name = "Kategorie", value = voiceClient.channel.category.name)
    data.add_field(name = "Verbundene Nutzer", value = len(voiceClient.channel.members))
    
    
    data.add_field(name = "Bitrate", value = str(int(voiceClient.channel.bitrate / 1000)) + "kbps")
    data.add_field(name = "Latenz", value = str(round((voiceClient.latency * 1000), 2)) + "ms")
    data.add_field(name = "Nutzer-Limit", value = voiceClient.channel.user_limit)
    
    data.add_field(name = "Endpoint", value = voiceClient.endpoint, inline = False)
    
    data.set_author(name = "🔊 Voice-Info")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(voiceClient.channel.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)

def _compareDate(first, second):
    if first.month < second.month or first.day < second.day :
        return 1

    if first.month > second.month or first.day > (second.day + 6):
        return 2
        
    return 0

def _appendItem(itemList, day, start, end, summary):
    itemList[day].append("`" + start.strftime("%H:%M") + " - " + end.strftime("%H:%M` ") + summary + "\n")

async def wochenplan(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt den Wochenplan an.
    !wochenplan {DATUM}
    {DATUM} <leer>, TT.MM.JJJJ
    !wochenplan\r!wochenplan 05.05.2021
    """
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds = 7200)
    if len(message.content) > 12:
        try:
            date = message.content.split(" ")[1]
            items = date.split(".")
            now = datetime.datetime(int(items[2]), int(items[1]), int(items[0]), 0, 0, 0, tzinfo = datetime.timezone.utc)
        except:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "wochenplan"))      
            return         
    
    content = ""
    with open(botData.modulesDirectory + "data/calendar/cal.ical", "r") as f:
        content += f.read()
        
    calendar = Calendar.from_ical(content)

    weekdayItems = [[], [], [], [], [], [], []]
    startOfWeek = now - datetime.timedelta(days = now.weekday())
    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.decoded("summary").decode("utf-8").replace("Höhere Mathematik", "HM").replace("Elektromagnetische Felder", "EMF").replace("Komplexe Analysis und Integraltransformationen", "KAI") 
            dtstart = component.decoded("dtstart")
            dtend = component.decoded("dtend")
            
            if "rrule" in component:
                if (dtstart - startOfWeek).days > 7:
                    continue
                
                if "UNTIL" in component.decoded("rrule"):
                    if (component.decoded("rrule")["UNTIL"][0] - now).days < 0:
                        continue
                        
                if "COUNT" in component.decoded("rrule"):
                    intervalModifier = 1
                    if "INTERVAL" in component.decoded("rrule"):
                        intervalModifier = component.decoded("rrule")["INTERVAL"][0]
                    if (dtstart + datetime.timedelta(days = (7 * intervalModifier * component.decoded("rrule")["COUNT"][0])) - now).days < 0:
                        continue
                
                if "INTERVAL" in component.decoded("rrule"):
                    if (abs(startOfWeek.isocalendar()[1] - dtstart.isocalendar()[1]) % component.decoded("rrule")["INTERVAL"][0]) is 0:
                        _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                        continue
                    
                
                if "BYDAY" in component.decoded("rrule"):
                    if len(component.decoded("rrule")["BYDAY"]) > 1:
                        for i in range(len(component.decoded("rrule")["BYDAY"])):
                            appendDate = True
                            weekdayIndex = { "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6 }
                            indexDay = weekdayIndex[component.decoded("rrule")["BYDAY"][i]]
                            datetimeDay = startOfWeek + datetime.timedelta(days = indexDay)
                            if "exdate" in component:
                                if hasattr(component.decoded("exdate"), "dts"):
                                    for vDDDType in component.decoded("exdate").dts:
                                        if (vDDDType.dt - datetimeDay).days is 0:
                                            appendDate = False
                                            break
                                else:   
                                    for exdate in component.decoded("exdate"):
                                        for vDDDType in exdate.dts:
                                            if (vDDDType.dt.date() - datetimeDay.date()).days is 0:
                                                appendDate = False
                                                break

                            if appendDate:
                                if (datetimeDay - dtend).days >= -1:
                                    _appendItem(weekdayItems, indexDay, dtstart, dtend, summary)
                            continue
                        
                if "exdate" in component:
                    returnToMainloop = False
                    if hasattr(component.decoded("exdate"), "dts"):
                        for vDDDType in component.decoded("exdate").dts:
                            if (vDDDType.dt - startOfWeek).days < 7:
                                returnToMainloop = True
                                break
                    else:   
                        for exdate in component.decoded("exdate"):
                            for vDDDType in exdate.dts:
                                if (vDDDType.dt - startOfWeek).days < 7:
                                    returnToMainloop = True
                                    break
                    
                    if not returnToMainloop:
                        _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                    continue
                    
                _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                continue    
                
                        
            if component.content_line("dtend", dtend)[-6:] == "+00:00":
                dtstart += datetime.timedelta(hours = 2)
                dtend += datetime.timedelta(hours = 2)
            if _compareDate(dtstart, startOfWeek) is not 0:
                continue
            else:
                _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
    
    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = startOfWeek.strftime("Woche vom %d.%m.%Y (KW %U)")
    )
    
    items = ""
    weekdayNames = [ "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag" ]
    for i in range(7):
        weekdayItems[i] = sorted(weekdayItems[i], key = lambda x: int(x[1:3]))
        dayString = ""
        for entry in weekdayItems[i]:
            dayString += entry
                
        data.add_field(name = weekdayNames[i] + (startOfWeek + datetime.timedelta(days = i)).strftime(" `(%d.%m.%Y)`"), value = dayString if dayString is not "" else "-", inline = False)
    
    data.set_author(name = "🗓️ Wochenplan für ETIT")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Vorlesung, wenn nicht anderweitig angegeben.\nJegliche Angaben ohne Gewähr.\nStand: {}".format(modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)