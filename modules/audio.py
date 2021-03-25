import asyncio
import discord
import json
import modules.bottiHelper
import modules.data.ids as ids
import os
import time

global audioSourceFile
musicQueue = []

async def _checkForVoiceClient(botti, message, string):
    voiceClients = botti.voice_clients
    if not voiceClients:
        await modules.bottiHelper._sendMessagePingAuthor(message, string)
        return None
    for x in range(len(voiceClients)):
        if message.guild.name is voiceClients[x].guild.name:
            voiceClient = voiceClients[x]
            return voiceClient

async def connect(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl verbindet den Bot mit einen Sprach-Kanal.
    !connect
    """
    try:
        voiceClients = botti.voice_clients
        if voiceClients:
            await disconnect(botti, botData, message)
        voiceClient = await message.author.voice.channel.connect(timeout=10, reconnect=True)
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":loud_sound: Zu **'{0}'** verbunden!".format(voiceClient.channel.name))
        return True
    except Exception:
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Du befindest dich in keinem Sprach-Kanal!")
        return False

async def disconnect(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl trennt den Bot vom Sprach-Kanal.
    !disconnect
    """
    voiceClient = await _checkForVoiceClient(botti, message, ":x: Der Bot ist zu keinem Sprach-Kanal verbunden!")
    if voiceClient is None:
        return
    await voiceClient.disconnect()
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":loud_sound: Verbindung zu **'{0}'** getrennt!".format(voiceClient.channel.name))

async def pause(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl pausiert die Audioausgabe des Bots.
    !pause
    """
    voiceClient = await _checkForVoiceClient(botti, message, ":x: Der Bot ist zu keinem Sprach-Kanal verbunden!")
    if voiceClient is None:
        return
    if not voiceClient.is_playing() or voiceClient.is_paused():
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Gerade spielt keine Musik!")
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":pause_button: Playback pausiert!")
        voiceClient.pause()

def _downloadVideoJSON(botData, url):
    return os.system("youtube-dl --quiet --no-playlist --write-info-json --skip-download --output \"{0}/temp/%(id)s\" {1}".format(botData.modulesDirectory, url))    

async def play(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl spielt ein Youtube-Video ab.
    !play {PARAMS} {YT-URL}
    {YT-URL} String [Youtube-URL]
    {PARAMS} "-q" [Quiet-Mode]
    !play https://www.youtube.com/watch?v=dQw4w9WgXcQ\r!play -q https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """
    voiceClients = botti.voice_clients
    if not voiceClients:
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Bot befindet sich in keinem Sprach-Kanal. Versuche zu dir zu verbinden...")
        if await connect(botti, botData, message) is not True:
            return
        voiceClients = botti.voice_clients
    for x in range(len(voiceClients)):
        if message.guild.name is voiceClients[x].guild.name:
            voiceClient = voiceClients[x]
    
    if voiceClient.is_playing() or voiceClient.is_paused():
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Bot hat bereits Musik geladen. Nutze zuerst `!stop`, um ein weiteres Musikstück abspielen zu können!")
        return
        
    parameters = modules.bottiHelper._getParametersFromMessage(message.content, 15)
    subcommand = 6 + (len(parameters) * 3) 
    
    url = message.content[subcommand:]
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":arrow_down: Lade herunter... Dies kann eine kurze Weile dauern!")
    _downloadVideoJSON(botData, url)
    status = os.system("youtube-dl --quiet --no-playlist --extract-audio --audio-format opus --audio-quality 0 --output \"{0}/temp/%(id)s.opus\" {1}".format(botData.modulesDirectory, url))
    global audioSourceFile
    try:
        if status == 1:
            raise FileNotFoundError()
        id = message.content.split("=")[1]
        audioSourceFile = botData.modulesDirectory + "temp/{}.opus".format(id)
        voiceClient.play(discord.FFmpegPCMAudio(source = audioSourceFile))
        with open(botData.modulesDirectory + "data/config/FFmpegPlayer.botti") as volumeFile:
            volumeLevel = volumeFile.readline().rstrip()
        voiceClient.source = discord.PCMVolumeTransformer(voiceClient.source)
        voiceClient.source.volume = float(volumeLevel)
        
        if "q" in parameters:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":play_pause: Spiele Musik mit Lautsärke **{0}**...".format(float(volumeLevel)))
        else:
            with open(botData.modulesDirectory + "temp/" + id + ".info.json") as jsonInfo:
                jsonData = json.load(jsonInfo)
                
                data = discord.Embed(
                    title = "<:youtube:" + str(ids.emojiIDs.youtube_EmojiID) + "> Youtube-Video",
                    color = 0xff0000,
                    description = ""
                )
                
                data.add_field(name = ":bookmark_tabs: Titel", value = jsonData["title"])
                data.add_field(name = ":man_raising_hand: Uploader", value = jsonData["uploader"])
                data.add_field(name = ":clock1: Dauer", value = time.strftime('%H:%M:%S', time.gmtime(int(jsonData["duration"]))))
                
                data.add_field(name = ":eyes: Views", value = str("{:,}".format(int(jsonData["view_count"]))).replace(",", " "))
                data.add_field(name = ":thumbsup: Likes", value = str("{:,}".format(int(jsonData["like_count"]))).replace(",", " "))
                data.add_field(name = ":thumbsdown: Dislikes", value = str("{:,}".format(int(jsonData["dislike_count"]))).replace(",", " "))

                data.add_field(name = ":date: Uploaddatum", value = "{}.{}.{}".format(jsonData["upload_date"][6:8], jsonData["upload_date"][4:6], jsonData["upload_date"][:4]))
                data.add_field(name = ":dividers: Kategorien", value = jsonData["categories"])
                data.add_field(name = ":loud_sound: Lautstärke", value = str(float(volumeLevel)))
                
                data.add_field(name = ":card_box: Tags", value = jsonData["tags"], inline = False)
                
                data.set_thumbnail(url = jsonData["thumbnails"][0]["url"])
                data.set_footer(text = "ID: {0}\nStand: {1}".format(id, modules.bottiHelper._getTimestamp()))               
                
                await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!play"))
    except FileNotFoundError:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Es ist ein Fehler aufgetreten! Achte darauf, dass die URL richtig ist, und nur die Video-ID darin enhalten ist (also z.B. kein `&t=`)")

async def queue(botti, botData, message):
    try:
        option = message.content.split(" ")[1]
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!queue"))      
        return
        
    global musicQueue
    
    if option == "list":
        if len(musicQueue) == 0:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: Die Warteschlange ist leer!")
            return
        else:
            queueElements = "```markdown\n"
            for i in range(0, len(musicQueue)):
                with open(botData.modulesDirectory + "temp/" + musicQueue[i].split("?v=")[1] + ".info.json") as jsonInfo:
                    jsonData = json.load(jsonInfo)
                    queueElements += str(i + 1) + ") " + jsonData['title'] + " [" + jsonData['uploader'] + "] | " + musicQueue[i] + "\n"
            queueElements += "```"
            await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: Die Warteschlange ist:\n{}".format(queueElements))
            return
    elif option == "add":
        try:
            status = _downloadVideoJSON(botData, message.content.split(" ")[2])
            if status == 1:
                raise FileNotFoundError()
            musicQueue.append(message.content.split(" ")[2])
            await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: Video mit ID `{}` wurde zur Warteschlange hinzugefügt!".format(message.content.split(" ")[2].split("?v=")[1]))
            return
        except FileNotFoundError:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Es ist ein Fehler aufgetreten! Achte darauf, dass die URL richtig ist, und nur die Video-ID darin enhalten ist (also z.B. kein `&t=`)")
            return
    elif option == "remove":
        try:
            removeIndex = int(message.content.split(" ")[2])
            if removeIndex < 1 or removeIndex > len(musicQueue):
                await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: Ungültiger Warteschlangen-Index!")
                return
        except:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!queue"))      
            return              
        await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: {} wird aus der Warteschlange entfernt!".format(musicQueue[removeIndex - 1]))
        del musicQueue[removeIndex - 1]
        return
    elif option == "next":
        if len(musicQueue) <= 1:
            await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: Nicht genügend Elemente in der Warteschlange!")
            return       
        del musicQueue[0]
        await modules.bottiHelper._sendMessagePingAuthor(message, ":minidisc: Es wird zum nächsten Lied gesprungen!")
    elif option == "play":
        dummyMessage = modules.bottiHelper._createDummyMessage(message.author, message.channel, "!play " + musicQueue[0])
        await play(botti, botData, dummyMessage)
        pass

async def reconnect(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl verbindet erneut zum Sprach-Kanal.
    !reconnect
    """
    voiceClient = await _checkForVoiceClient(botti, message, ":x: Der Bot ist zu keinem Sprach-Kanal verbunden!")
    if voiceClient is None:
        return
    await voiceClient.disconnect()
    await voiceClient.channel.connect(timeout=10, reconnect=True)
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":loud_sound: Erneut zu **'{0}'** verbunden!".format(voiceClient.channel.name))

async def resume(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl führt die Audio-Wiedergabe fort.
    !resume
    """
    voiceClient = await _checkForVoiceClient(botti, message, ":x: Der Bot ist zu keinem Sprach-Kanal verbunden!")
    if voiceClient is None:
        return
    if voiceClient.is_playing() or not voiceClient.is_paused():
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Gerade ist keine Musik angehalten!")
    else:
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":arrow_forward: Playback fortgeführt!")
        voiceClient.resume()

async def stop(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl stoppt die Audio-Wiedergabe.
    !stop
    """
    voiceClient = await _checkForVoiceClient(botti, message, ":x: Der Bot ist zu keinem Sprach-Kanal verbunden!")
    if voiceClient is None:
        return
    if not voiceClient.is_playing() or voiceClient.is_paused():
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Gerade spielt keine Musik!")
    else:
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":stop_button: Playback beendet!")
        voiceClient.stop()

async def volume(botti, botData, message):
    """
    Reserviert für Entwickler
    Dieser Befehl ändert die Lautstärke des Bots.
    !volume {VOLUME}
    {VOLUME} 0.0 - 2.0
    !volume 1.0
    """
    voiceClient = await _checkForVoiceClient(botti, message, ":x: Der Bot ist zu keinem Sprach-Kanal verbunden!")
    if voiceClient is None:
        return
    global audioSourceFile
    try:
        volumeLevel = message.content.split(" ")[1]
        voiceClient.source.volume = float(volumeLevel)
        with open(botData.modulesDirectory + "data/config/FFmpegPlayer.botti", "w") as volumeFile:
            volumeFile.write(volumeLevel)
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":loud_sound: Lautsärke auf **{0}** gesetzt!".format(volumeLevel))
    except IndexError:
        with open(botData.modulesDirectory + "data/config/FFmpegPlayer.botti", "r") as volumeFile:
            volumeLevel = volumeFile.readline().rstrip()
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":loud_sound: Lautsärke bei **{0}**!".format(volumeLevel))
