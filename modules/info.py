import datetime
import discord
import json
import modules.bottiHelper
import modules.calendar
import modules.construct
import modules.data.ids as ids
import os
import platform
import psutil
import requests

from mcstatus import MinecraftServer

class Quicklink():
    def __init__(self, pName, pURL, pTitle, pThumbnail = None, pColor = 0x009AFF):
        self.name = pName
        self.URL = pURL
        self.title = pTitle
        self.thumbnail = pThumbnail
        self.color = pColor

def _format(content, botData, embed):
    replacementDict = {
        "<p>":      "",
        "</p>":     "",
        "<strong>": "**",
        "</strong>":"**",
        "<em>":     "_",
        "</em>":    "_",
        "<div>":    "",
        "</div>":   "",
        "&nbsp;":   ""
    }
    
    for key in replacementDict.keys():
        content = content.replace(key, replacementDict[key])
        
    if "<img" in content:
        urlStart = content[(content.find("src=\"") + 6):] # 6 = len("src=\"")
        url = urlStart[:urlStart.find("\"")]
        
        content = content[:content.find("<img")] + content[(content.find("/>") + 2):]
    
        embed.set_image(url = (botData.fachschaftURL + url))
    
    while (content.find("<") != -1) and (content.find(">") != -1):
        print(content)
        print("\n")
        content = content[:content.find("<")] + content[(content.find(">") + 1):]
        print(content)
        print("\n\n\n\n\n")
    
    return content[:(1012-len(botData.fachschaftURL))] # 1012 = 1024 - len(" [...mehr]()") | 1024 = max embed value length

def _getContent(content, botData):
    stringIndex = content.find("spField") + 9 # 9 = len("spField'>")
    content = content[stringIndex:]
    return content[:content.find("</div>")]

def _getLastEdited(content):
    stringIndex = content.find("spEntriesListTitleTag") + 32 # 32 = len("spEntriesListTitleTag>          ")
    return content[stringIndex:stringIndex + 30] # 30 = len("Zuletzt bearbeitet: DD.MM.YYYY")

def _getTitle(content, botData):
    stringIndex = content.find("spEntriesListTitle") + 30 # 30 = len("spEntriesListTitle> <a href='/")
    tagInfo = content[stringIndex:]
    url = tagInfo[:tagInfo.find("\"")]
    title = tagInfo[(len(url) + 2):tagInfo.find("</a>")] # 2 = len("'>")
    
    return "[{title}]({baseURL}{url})".format(title = title, url = url, baseURL = botData.fachschaftURL)

async def _printNews(message, botData, post):
    data = discord.Embed(
        title = "",
        description = "",
        color = 0xeeeeee,
        
    )
    websiteContent = requests.get(botData.fachschaftURL).text
    
    news = websiteContent.split("<div class=\"spEntriesListContainer\">")[1].split("<div style=\"clear:both;\">")[post]
    
    title = _getTitle(news, botData)        
    data.title = title[1:].split("]")[0]
    data.url = title.split("](")[1][:-1]
    
    content = _format(_getContent(news, botData), botData, data)
    data.add_field(name = "Neues aus der Fachschaft", value = content + " [...mehr]({})".format(botData.fachschaftURL))
    
    data.set_thumbnail(url = botData.fachschaftURL + "templates/joomlakit/images/britzel-white.png")
    
    lastEdited = _getLastEdited(news)
    data.set_footer(text = "{}".format(lastEdited))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

async def botinfo(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Botinfo an.
    !botinfo
    """
    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = botti.user.mention
    )
    data.add_field(name = "Präfix", value = botData.botPrefix)
    data.add_field(name = "Name", value = botti.user.name)
    data.add_field(name = "Discriminator", value = str(("#" + botti.user.discriminator)))
    
    data.add_field(name = "Sprache", value = "Deutsch")
    data.add_field(name = "Vertretene Server" , value = str(len(botti.guilds)))
    data.add_field(name = "OS", value = platform.system() + "-" + str(os.name).upper() + "-" + platform.release())
    
    data.add_field(name = "discord.py Version", value = discord.__version__)
    data.add_field(name = "Latenz", value = str(round((botti.latency * 1000), 2)) + "ms")
    data.add_field(name = "Entwickler", value = "<@!{itzFlubbyID}>".format(itzFlubbyID = ids.userIDs.ITZFLUBBY))
    
    data.add_field(name = "GitHub", value = "https://github.com/itzFlubby/ETIT-Chef/", inline = False)
    
    data.set_author(name = "🤖 Bot-Info")
    data.set_thumbnail(url = botti.user.avatar.url)
    data.set_footer(text = "ID: {0}\nBei Verbesserungsvorschlägen: !vorschlag <NACHRICHT>\nStand: {1}".format(str(botti.user.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
        description = channelToGetInfo.mention
    )
    data.add_field(name = "Name", value = channelToGetInfo.name)
    data.add_field(name = "Typ", value = channelToGetInfo.type)
    data.add_field(name = "Position", value = str(channelToGetInfo.position + 1))
    
    data.add_field(name = "Erstellt am", value = modules.bottiHelper._toUTCTimestamp(channelToGetInfo.created_at))
    data.add_field(name = "Slow-Modus", value = str(channelToGetInfo.slowmode_delay) + "s") 
    data.add_field(name = "Mitglieder", value = str(len(channelToGetInfo.members))) 
    
    data.add_field(name = "NSFW", value = channelToGetInfo.is_nsfw()) 
    data.add_field(name = "NEWS", value = channelToGetInfo.is_news()) 
    data.add_field(name = "Kategorie-ID", value = str(channelToGetInfo.category_id)) 
    
    data.add_field(name = "Thema", value = channelToGetInfo.topic, inline = False)
    
    data.set_author(name = "💬 Kanal-Info")
    data.set_thumbnail(url = message.guild.icon.url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(channelToGetInfo.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

async def corona(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt Informationen über das Corona-Virus an.
    !corona
    """
    output = requests.get(botData.coronaAPI["url"])
    
    jsonData = json.loads(output.content.decode('utf8'))["features"][0]["attributes"]
    
    data = discord.Embed(
        title = "{bez} {gen}".format(bez = jsonData["BEZ"], gen = jsonData["GEN"]),
        description = "{debkg_id} {nuts}".format(debkg_id = jsonData["DEBKG_ID"], nuts = jsonData["NUTS"]),
        color = 0xf55d42
    )
    
    data.add_field(name = "7 Tage Inzidenz (pro 100k)\n{county}".format(county = jsonData["county"]), value = "{:.2f}".format(jsonData["cases7_per_100k"]))
    data.add_field(name = "⠀\n{bl}".format(bl = jsonData["BL"]), value = "{:.2f}".format(jsonData["cases7_bl_per_100k"]))
    data.add_field(name = "⠀", value = "⠀") # spacer
    data.add_field(name = "Neuinfektionen pro Woche\n{county}".format(county = jsonData["county"]), value = jsonData["cases7_lk"])
    data.add_field(name = "⠀\n{bl}".format(bl = jsonData["BL"]), value = jsonData["cases7_bl"])
    data.add_field(name = "⠀", value = "⠀") # spacer
    data.add_field(name = "Todesfälle pro Woche\n{county}".format(county = jsonData["county"]), value = jsonData["death7_lk"])
    data.add_field(name = "⠀\n{bl}".format(bl = jsonData["BL"]), value = jsonData["death7_bl"])
    data.add_field(name = "⠀", value = "⠀") # spacer
    
    data.add_field(name = "⠀", value = "[Quelle]({source})\n[Thumbnail-Quelle]({thumbnail})".format(source = botData.coronaAPI["source"], thumbnail = botData.coronaAPI["thumbnail"]))
    data.set_thumbnail(url = botData.coronaAPI["thumbnail"])
    data.set_footer(text = "Letztes Update: {updateTimestamp}.\nJegliche Angaben ohne Gewähr.".format(updateTimestamp = jsonData["last_update"]))
    
    await modules.bottiHelper._sendMessagePingAuthor(message, embed = data)

async def fachschaft(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt Info über die Fachschaft an.
    !fachschaft {OPTION} {PARAMS}
    {OPTION} "news", "link", "sitzung", "öffnungszeiten"
    {PARAMS} <leer>, Newspost in range(7)
    !fachschaft news\r!fachschaft news 1
    """
    options = message.content.split(" ")
    if len(options) == 2:
        if options[1].lower() == "news":
            await _printNews(message, botData, 0) # 0 : latest post
        elif options[1].lower() == "link":
            data = discord.Embed(
                title = "Fachschaft ETEC",
                color = 0x009AFF,
                description = "",
                url = botData.fachschaftURL
            )
            
            data.set_author(name = "🌐 Shortcut Link")   
            data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
            data.set_thumbnail(url = botData.fachschaftURL + "templates/joomlakit/images/britzel-white.png")
            await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)
            
        elif options[1].lower() == "sitzung":
            data = discord.Embed(
                title = "Fachschafts-Sitzung ETEC",
                color = 0x009AFF,
                description = "",
                url = botData.fachschaftSitzungURL
            )
            
            data.set_author(name = "🌐 Shortcut Link")   
            data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
            data.set_thumbnail(url = botData.fachschaftURL + "templates/joomlakit/images/britzel-white.png")
            await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)
        elif options[1].lower() == "öffnungszeiten":
            dates = modules.calendar._getOpenTimes(botData)
            
            data = modules.construct._constructDefaultEmbed(
                title = "Anstehende Öffnungszeiten der Fachschaft",
                color = 0x009AFF,
                description = "",
                url = botData.fachschaftCalendarURL,
                thumbnail = botData.fachschaftURL + "templates/joomlakit/images/britzel-white.png"
            )
            
            weekdayReplace = {
                "Monday": "Montag",
                "Tuesday": "Dienstag",
                "Wednesday": "Mittwoch",
                "Thursday": "Donnerstag",
                "Friday": "Freitag",
                "Saturday": "Samstag",
                "Sunday": "Sonntag",   
            }
            
            for component in dates:
                date = component.decoded("dtstart").strftime("%A, %d.%m.%Y")
                for key in weekdayReplace.keys():
                    date = date.replace(key, weekdayReplace[key])
                data.add_field(name = date, value = component.decoded("summary").decode("utf-8") + "\n`" + component.decoded("dtstart").strftime("%H:%M") + " - " + component.decoded("dtend").strftime("%H:%M`"))
            
            data.add_field(name = "⠀", value = "[Thumbnail-Quelle]({url})".format(url = data.thumbnail.url), inline = False)
            await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "fachschaft"))

    elif len(options) == 3:
        if options[1].lower() == "news":
            if not (options[2].isdigit()) or int(options[2]) > 7:
                await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "fachschaft"))
                return
                
            await _printNews(message, botData, int(options[2]))
        else:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "fachschaft"))

    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "fachschaft"))

async def listroles(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl listet Rollen mit ihrer Mitgliederzahl auf.
    !listroles
    """
                          # MATH                 ELEK      INFO    TM
    includeRoleColors = [ 0x00b0f0, 0x3ed5e3, 0xffc000, 0x92d050, 0xe67e22 ]
    includeRoleNames = [ "Bachelor", "Master" ]
    
    totalStrings = []
    totalString = ":receipt: Rollen-Übersicht: \n```ml\n           Rollen-Name           | Mitgliederzahl\n=================================================\n"
    
    for role in message.guild.roles:
        if role.color.value in includeRoleColors or (True in [roleName in role.name for roleName in includeRoleNames]):
            roleName = role.name
            if len(roleName) > 33: # 33 = len("           Rollen-Name           ")
                roleName = roleName[:30] + "..." # 30 = len("           Rollen-Name           ") - len("...")
                
            totalString += "{:<33}| {:<4}\n".format(roleName, modules.bottiHelper._spaceIntToString(len(role.members)))
           
            if len(totalString) > botData.maxMessageLength:
                totalStrings.append(totalString + "```")
                totalString = "```ml\n"
                    
    totalStrings.append(totalString + "```")
        
    for string in totalStrings:
        await modules.bottiHelper._sendMessage(message, string) 

async def minecraft(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Minecraft-Server-Info an.
    !minecraft
    """    
    data = discord.Embed(
        title = "{emoji} Server-Status".format(emoji = modules.construct._constructEmojiString(ids.emojiIDs.MINECRAFT)),
        color = 0x00ff00,
        description = botData.minecraftServerName
    )
    data.set_thumbnail(url = botti.user.avatar.url)
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
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

async def permissions(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die Berechtigungen für einen Nutzer an.
    !permissions {@USER}
    {@USER} "", Nutzer-Erwähnung
    !permissions\r!permissions @ETIT-Chef
    """
    permissionsObject = None
    isUser = True
    if len(message.role_mentions) > 0:
        isUser = False
        permissionsObject = message.role_mentions[0]
        standardPerms = list(permissionsObject.permissions)
    else:
        permissionsObject = message.author
        if len(message.mentions) != 0:
            permissionsObject = message.mentions[0]
        standardPerms = None

    channelPermissionsList = []
    for textChannel in message.guild.text_channels:
        channelMentionStrig = textChannel.mention
        overwrites = textChannel.permissions_for(permissionsObject) if isUser else iter(textChannel.overwrites_for(permissionsObject).pair()[0]) + standardPerms
        permissionType = 0
        if overwrites.read_messages:
            permissionType += 1
        if overwrites.send_messages:
            permissionType += 2
        channelPermissionsList.append([channelMentionStrig, permissionType])
     
    permissionTypeToEmoji = {
        0: modules.construct._constructEmojiString(ids.emojiIDs.DND) + " Keine Rechte",
        1: modules.construct._constructEmojiString(ids.emojiIDs.IDLE) + " Lese Rechte",
        2: modules.construct._constructEmojiString(ids.emojiIDs.OFFLINE) + " Undefinierte Rechte", # SHOULD never occur
        3: modules.construct._constructEmojiString(ids.emojiIDs.ONLINE) + " Lese- und Schreibrechte"
    }
    
    partialFieldStrings = [[], [], [], []]
    
    formattedString = ":shield: Berechtigungen in Text-Kanälen für {permissionsObjectMention}\n".format(permissionsObjectMention = permissionsObject.mention)
    for element in channelPermissionsList:
        channelMentionStrig = element[0]
        permissionType = element[1]
        
        partialFieldStrings[permissionType].append(channelMentionStrig + "\n")

    data = discord.Embed(
        title = "",
        color = 0x123456,
        description = ""
    )

    for run, permissionsTypeList in enumerate(partialFieldStrings):
        if len(permissionsTypeList) == 0:
            continue
        
        partialFieldString = ""
        for channelMention in permissionsTypeList:
            if len(partialFieldString + channelMention) > 1024:
                data.add_field(name = permissionTypeToEmoji[run], value = partialFieldString)
                partialFieldString = ""
            partialFieldString += channelMention
        data.add_field(name = permissionTypeToEmoji[run], value = partialFieldString)
        
    data.set_author(name = "📜 Berechtigungen")
    data.set_thumbnail(url = botti.user.avatar.url)
    data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message, embed = data)
            
async def ping(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die WebSocket-Protokoll-Latenz an.
    !ping
    """
    await modules.bottiHelper._sendMessagePingAuthor(message, ":satellite: Die Discord WebSocket-Protokoll-Latenz liegt bei **{0}ms**!".format(str(round((botti.latency * 1000), 2)))) 

async def quicklink(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl schickt einen Quicklink.
    !quicklink {LINK}
    {LINK} "dontask", "exmatrikulation", "kw", "duden", "github", "stackoverflow"
    !quicklink dontask\r!quicklink duden
    """
    linksDict = {
        "dontask": Quicklink(
                        "dontask", 
                        "https://dontasktoask.com/", 
                        "Don't ask to ask, just ask!", 
                        "https://dontasktoask.com/favicon.png"
                    ),
        "exmatrikulation": Quicklink(
                        "exmatrikulation", 
                        "https://www.sle.kit.edu/imstudium/exmatrikulation.php", 
                        "Wiederschauen und reingehauen!", 
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Logo_KIT.svg/800px-Logo_KIT.svg.png", 
                        0x009682
                    ),
        "kw": Quicklink(
                        "kw", 
                        "https://generationstrom.com/2020/01/07/kw-oder-kwh/", 
                        "KW oder KWh?", 
                        "https://i1.wp.com/generationstrom.com/wp-content/uploads/2017/07/generationstrom_avatar_v2.png"
                    ),
        "duden": Quicklink(
                        "duden", 
                        "https://www.duden.de/", 
                        "Aufschlagen, nachschlagen, zuschlagen. Duden.", 
                        "https://www.duden.de/modules/custom/duden_og_image/images/Duden_FB_Profilbild.jpg", 
                        0xFBC53E
                    ),
        "github": Quicklink(
                        "github", 
                        "https://github.com/itzFlubby/ETIT-Chef/", 
                        "ETIT-Chef Github", 
                        "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", 
                        0xFEFEFE
                    ),
        "stackoverflow": Quicklink(
                        "stackoverflow", 
                        "https://stackoverflow.com/", 
                        "Hippety hoppety your code is now my property!", 
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Stack_Overflow_icon.svg/768px-Stack_Overflow_icon.svg.png", 
                        0xEF8236
                    ),
        "reddit": Quicklink(
                        "reddit",
                        "https://www.reddit.com/r/KaIT/",
                        "r/KaIT",
                        "https://www.redditinc.com/assets/images/site/reddit-logo.png",
                        0xFF5700
                    )
    }
    
    arguments = message.content.split(" ")
    if len(arguments) != 2:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "quicklink"))
        return
        
    quicklink = arguments[1]
    
    if quicklink not in linksDict.keys():
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "quicklink"))
        return
        
    data = discord.Embed(
        title = linksDict[quicklink].title,
        color = linksDict[quicklink].color,
        description = linksDict[quicklink].URL,
        url = linksDict[quicklink].URL
    )
    
    if linksDict[quicklink].thumbnail is not None:
        data.set_thumbnail(url = linksDict[quicklink].thumbnail)
        data.add_field(name = "⠀", value = "[Thumbnail-Quelle]({link})".format(link = linksDict[quicklink].thumbnail))

    data.set_author(name = "🌐 Shortcut Link")   
    data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
        description = role.mention
    )
    data.add_field(name = "Name", value = role.name)
    data.add_field(name = "Position", value = str(role.position))
    data.add_field(name = "Gruppiert", value = str(role.hoist))
    
    data.add_field(name = "Rolle erstellt am", value = modules.bottiHelper._toUTCTimestamp(role.created_at))
    data.add_field(name = "Farbe", value = hex(role.color.value))
    data.add_field(name = "Mitglieder", value = len(role.members))
    
    data.add_field(name = "Erwähnbar", value = str(role.mentionable))
    data.add_field(name = "Standard", value = str(role.is_default()))
    
    data.set_author(name = "🧾 Rollen-Info")
    data.set_thumbnail(url = message.guild.icon.url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(role.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
    data.add_field(name = "Eigentümer", value = message.guild.owner.mention)
    
    data.add_field(name = "Mitglieder", value = message.guild.member_count)
    data.add_field(name = "Rollen", value = len(message.guild.roles))
    data.add_field(name = "Emojis", value = len(message.guild.emojis))
    
    data.add_field(name = "Kategorien", value = len(message.guild.categories))
    data.add_field(name = "Text-Kanäle", value = len(message.guild.text_channels))
    data.add_field(name = "Sprach-Kanäle", value = len(message.guild.voice_channels))
    
    data.add_field(name = "Erstellt am", value = modules.bottiHelper._toUTCTimestamp(message.guild.created_at), )
    
    data.add_field(name = "Icon", value = message.guild.icon.url, inline = False)
    
    data.set_author(name = "📱 Server-Info")
    data.set_thumbnail(url = message.guild.icon.url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(message.guild.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
        data.set_thumbnail(url = botti.user.avatar.url)
    
    data.set_author(name = "📑 Stats")
    data.set_footer(text = "Stand: {0}".format(modules.bottiHelper._getTimestamp()))
  
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

async def test(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl überprüft, ob der Bot online ist.
    !test
    """
    botMessage = await modules.bottiHelper._sendMessagePingAuthor(message, ":globe_with_meridians: Der Bot ist online und läuft ordnungsgemäß!")
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.NEIN))
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.DOCH))
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.OH))

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
    data.set_thumbnail(url = botti.user.avatar.url)
    data.set_footer(text = "Seitdem wurden {0} Befehle ausgeführt!\nStand: {1}".format(botData.befehlsCounter, modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
        description = user.mention
    )
    
    data.add_field(name = "Name", value = user.name)
    data.add_field(name = "Discriminator", value = "#{0}".format(user.discriminator))
    data.add_field(name = "Nick", value = user.nick)
    
    data.add_field(name = "Bot-User", value = user.bot)
    data.add_field(name = "Höchste Rolle", value = user.top_role)
    
    data.add_field(name = "Server beigetreten am", value = modules.bottiHelper._toUTCTimestamp(user.joined_at))
    data.add_field(name = "Account erstellt am", value = modules.bottiHelper._toUTCTimestamp(user.created_at))
    
    data.add_field(name = "Profilbild", value = user.avatar.url, inline = False)
    
    data.set_author(name = "👨‍🎓 User-Info")
    data.set_thumbnail(url = user.avatar.url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(user.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
    data.set_thumbnail(url = botti.user.avatar.url)
    data.set_footer(text = "ID: {0}\nStand: {1}".format(str(voiceClient.channel.id), modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)
    
async def zitate(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt die beliebtesten Zitate an.
    !zitate
    """
    citationRanking = []
    channel = message.guild.get_channel(ids.channelIDs.ZITATE)
    messages = await channel.history(limit=200).flatten()
    for cite in messages:
        if len(cite.reactions) > 0:
            highestReaction = sorted(cite.reactions, key = lambda reaction: reaction.count, reverse = True)[0]
            citationRanking.append([cite, highestReaction])
            
    citationRanking = sorted(citationRanking, key = lambda citation: citation[1].count, reverse = True)

    data = discord.Embed(
        title = "",
        color = 0x005dff,
        description = ""
    )
    
    for run, citation in enumerate(citationRanking[:10]):
        data.add_field(name = "Platz #{place}".format(place = (run+1)), value = "Festgehalten von {citation.author.mention} | {reaction.count} {reaction.emoji}\n{citation.content}".format(citation = citation[0], reaction = citation[1]), inline = False)

    data.set_author(name = "💬 Zitate-Ranking")
    data.set_thumbnail(url = message.guild.icon.url)
    data.set_footer(text = "Stand: {}".format(modules.bottiHelper._getTimestamp()))
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)