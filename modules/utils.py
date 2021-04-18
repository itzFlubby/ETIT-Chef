import copy
import datetime
import discord
import io
import modules.audio
import modules.banlist
import modules.bottiHelper
import modules.data.ids as ids
import modules.dev
import modules.gamble
import modules.info
import modules.lerngruppe
import modules.mensa
import modules.mod
import modules.guard
import modules.polls
import modules.roles
import modules.timer
import modules.utils

from os.path import exists
from PIL import Image, ImageFont, ImageDraw, ImageSequence 
from random import choice
from random import randint

async def antwortaufalles(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt dir die Antwort auf alles an.
    !antwortaufalles
    """
    await modules.bottiHelper._sendMessagePingAuthor(message, ":milky_way: Die Antwort auf die Frage nach dem Leben, dem Universum und dem ganzen Rest ist :four::two:!")

async def choose(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl wählt eine Option aus mehreren aus.
    !choose {OPTIONS}
    {OPTIONS} String;String;String;...
    !choose Nudeln;Spaghettit;Spätzle
    """
    await modules.bottiHelper._sendMessagePingAuthor(message, ":robot: Ich wähle **{0}** von **{1}**!".format(choice(str(message.content[8:]).split(';')), str(message.content[8:])))

async def command(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt eine Befehlshilfe an.
    !command {COMMAND}
    {COMMAND} String [Ein Befehl]
    !command !test\r!command test
    """
    try:
        commandName = message.content.split(" ")[1]
        if commandName[0] != "!":    
            commandName = "!" + commandName
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "command"))      
        return
        
    infoText = ""
    
    for i in range(0, botData.totalModules):
        if commandName in botData.fullCommandList[i]:
            infoText = getattr(botData.fullModuleList[i], commandName[1:]).__doc__
            break
    
    if infoText == None or infoText == "":
        infoText = "\n\nDieser Befehl existiert nicht, oder es ist keine Hilfe verfügbar!\nAusführung nicht verfügbar.\n"
    
    infoTextLines = infoText.replace("    ", "").split("\n")
    del(infoTextLines[0])
    del(infoTextLines[-1])
    
    data = discord.Embed(
        title = commandName,
        color = 0x009AFF,
        description = ""
    )
    data.set_author(name = "❓ Befehls-Hilfe") 
    data.set_thumbnail(url = botti.user.avatar_url)    
    data.set_footer(text = infoTextLines[0])
    
    data.add_field(name = "Beschreibung", value = infoTextLines[1] + "\n⠀", inline = False)
    data.add_field(name = "Ausführung", value = infoTextLines[2] + "\n⠀", inline = False)
    
    for i in range(3, len(infoTextLines)):
        if infoTextLines[i][0] == "{":
            commandParameters = infoTextLines[i].split("}")
            data.add_field(name = "Gültige Werte für " + commandParameters[0] + "}", value = commandParameters[1].replace("\r", "\n") + "\n⠀", inline = False)
        else:
            data.add_field(name = "Beispiel", value = infoTextLines[i].replace("\r", "\n") + "\n⠀", inline = False)
    
    await modules.bottiHelper._sendEmbedPingAuthor(message, "", embed = data)

async def convert(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl konvertiert einen Inhalt.
    !convert {INPUT-TYPE} {OUTPUT-TYPE} {INPUT}
    {INPUT-TYPE} "text", "bin", "hex"
    {OUTPUT-TYPE} "text", "bin", "hex"
    {INPUT} String, Bin, Hex
    !convert text bin Dieser String wird binär!\r!convert hex text 4963682062696e20746f6c6c21
    """
    try:
        convertFrom = message.content.split(" ")[1]
        convertTo = message.content.split(" ")[2]
        posInContent = 11 + len(convertFrom) + len(convertTo)
        textToConvert = message.content[posInContent:]
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "convert"))
        return     
       
    convertableFrom = [ "text", "bin", "hex" ]
    convertableTo = [ "bin", "text", "hex" ]
    convertIDs = [ 101, 103, 202, 203, 301, 302 ]
    # 101 : text -> bin
    # 103 : text -> hex
    # 202 : bin  -> text
    # 203 : bin  -> hex
    # 301 : hex  -> bin
    # 302 : hex  -> text
    
    convertID = -1
    
    for i in range(len(convertableFrom)):
        if convertFrom == "text":
            convertID = 100
            break
        if convertFrom == "bin":
            convertID = 200
            break
        if convertFrom == "hex":
            convertID = 300
            break
            
    if convertID == -1:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "convert"))      
        return        
    
    for i in range(len(convertableTo)):
        if convertTo == "bin":
            convertID += 1
            break
        if convertTo == "text":
            convertID += 2
            break    
        if convertTo == "hex":
            convertID += 3
            break    

    if convertID not in convertIDs:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "convert"))      
        return      

    try:
        if convertID == 101:
            convertResult = ' '.join(format(x, 'b') for x in bytearray(textToConvert, 'utf-8'))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":arrows_counterclockwise: '{0}' ist konvertiert (`{1} -> {2}`):\n{3}".format(textToConvert, convertFrom, convertTo, convertResult)) 
        
        if convertID == 103:
            convertResult = textToConvert.encode("utf-8").hex()
            await modules.bottiHelper._sendMessagePingAuthor(message, ":arrows_counterclockwise: '{0}' ist konvertiert (`{1} -> {2}`):\n{3}".format(textToConvert, convertFrom, convertTo, convertResult)) 
        
        if convertID == 202:
            binary_values = textToConvert.split(" ")
            convertResult = ""
            for binary_value in binary_values:
                convertResult += chr(int(binary_value, 2))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":arrows_counterclockwise: '{0}' ist konvertiert (`{1} -> {2}`):\n{3}".format(textToConvert, convertFrom, convertTo, convertResult))   
        
        if convertID == 203:
            binary_values = textToConvert.split(" ")
            convertResult = ""
            for binary_value in binary_values:
                convertResult += hex(int(binary_value, 2))
            await modules.bottiHelper._sendMessagePingAuthor(message, ":arrows_counterclockwise: '{0}' ist konvertiert (`{1} -> {2}`):\n{3}".format(textToConvert, convertFrom, convertTo, convertResult))   
        
        if convertID == 301:
            convertResult = bin(int(textToConvert, 16)).zfill(8) 
            await modules.bottiHelper._sendMessagePingAuthor(message, ":arrows_counterclockwise: '{0}' ist konvertiert (`{1} -> {2}`):\n{3}".format(textToConvert, convertFrom, convertTo, convertResult))   
 
        if convertID == 302:
            convertResult = bytes.fromhex(textToConvert).decode("utf-8")
            await modules.bottiHelper._sendMessagePingAuthor(message, ":arrows_counterclockwise: '{0}' ist konvertiert (`{1} -> {2}`):\n{3}".format(textToConvert, convertFrom, convertTo, convertResult)) 
    except ValueError:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Der Eingabetext ist nicht vom angegeben Typ `{}`".format(convertFrom))

async def flip(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl wirft eine Münze.
    !flip
    """
    if randint(1,2) == 1:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":coin: Die Münze ist auf :regional_indicator_k::regional_indicator_o::regional_indicator_p::regional_indicator_f: gelandet!")
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":coin: Die Münze ist auf :regional_indicator_z::regional_indicator_a::regional_indicator_h::regional_indicator_l: gelandet!")

async def help(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl zeigt die Befehls-Überischt an.
    !help
    """

    commandList = botData.fullCommandList.copy()
    moduleList = botData.fullModuleList.copy()
    moduleNames = botData.moduleNames.copy()
    
    if modules.guard._checkPermsQuiet(botti, message, modules.guard.allowed_roles) == False:
        commandList.remove(botData.audioCommandList)
        moduleList.remove(modules.audio)
        moduleNames.remove("audio")
        commandList.remove(botData.banlistCommandList)
        moduleList.remove(modules.banlist)
        moduleNames.remove("banlist")
        commandList.remove(botData.devCommandList)
        moduleList.remove(modules.dev)
        moduleNames.remove("dev")
        commandList.remove(botData.modCommandList)
        moduleList.remove(modules.mod)
        moduleNames.remove("mod")

    allHelpStrings = []
    helpStr = "```yaml\n"
    for i in range(len(moduleList)):
        moduleNameLen = len(moduleNames[i])
        spacerLen = int((19 - moduleNameLen) / 2)
        moduleHeader = ""    
        moduleHeader += "-"*spacerLen
        moduleHeader = moduleHeader + " " + moduleNames[i].upper() + " "
        if ((19 - moduleNameLen) % 2) == 0:
            moduleHeader += "-"*(spacerLen - 1)
        else:
            moduleHeader += "-"*spacerLen           
        moduleStr = "--------------------\n" + moduleHeader + "\n--------------------\n"
        for j in range(len(commandList[i])):
            infoText = getattr(moduleList[i], commandList[i][j].split("!")[1]).__doc__
            if infoText == None:
                infoText = "<NONE>\n<NONE>\n<NONE>\n<NONE>\n"
            infoTextLines = infoText.replace("    ", "").split("\n")
            del(infoTextLines[0])
            del(infoTextLines[-1])
            if len(infoTextLines[2]) < 19:
                infoTextLines[2] += " "*(19 - len(infoTextLines[2]))
            moduleStr += infoTextLines[2] + " " + infoTextLines[1] + "\n"
        
        if len(helpStr) + len(moduleStr) > 1900:
            allHelpStrings.append(helpStr)
            helpStr = "```yaml\n"
            
        helpStr += moduleStr 
    
    allHelpStrings.append(helpStr)
        
    if botti.get_user(message.author.id).dm_channel is None:
        await botti.get_user(message.author.id).create_dm()
         
    for string in allHelpStrings:
        await botti.get_user(message.author.id).dm_channel.send(string + "```")
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":question: Dir wurde eine Hilfe zugesandt!\n:question: Nutze den Befehl `!command {Unterbefehl}`, um Informationen über einen Befehl, wie dessen Ausführung ein Beispiel Eingaben zu erhalten!\n:question: Nutze zum Beispiel `!command !help`")

async def invite(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt einen Einladungslink an.
    !invite
    """    
    data =  discord.Embed(
        title = "",
        color = 0xcc0066,
        description = ""
    )
    data.set_author(name = "🥳 Einladung")
    data.set_thumbnail(url = message.guild.icon_url)
            
    invites = await message.guild.invites()
    
    for invite in invites:
        if invite.max_age == 0:
            data.add_field(name = "Permanent-Link", value = invite.url)
            data.set_footer(text = "Verwendungen: {0}\nErsteller: {1}#{2}".format(str(invite.uses), invite.inviter.name, str(invite.inviter.discriminator)))  
            await modules.bottiHelper._sendEmbedPingAuthor(message, "", embed = data)
            return
    
    invite = await message.channel.create_invite(max_age = 3600, unique = False, reason = "Requested by User.")       
    data.add_field(name = "Temporär-Link", value = invite.url)
    data.set_footer(text = "Gültigkeit: Eine Stunde\nErsteller: {0}#{1}".format(invite.inviter.name, str(invite.inviter.discriminator)))  
    await modules.bottiHelper._sendEmbedPingAuthor(message, "", embed = data)

async def kekse(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl... nunja... Kekse sind einfach toll!
    !kekse
    """
    botMessage = await modules.bottiHelper._sendMessage(message, "**Ich mag** :cookie::cookie::cookie: **OMNOMNOM**")
    await botMessage.add_reaction(":Nein:" + str(ids.emojiIDs.NEIN))
    await botMessage.add_reaction(":Doch:" + str(ids.emojiIDs.DOCH))
    await botMessage.add_reaction(":Oh:" + str(ids.emojiIDs.OH))
    await botMessage.add_reaction("🍪")

async def klausuren(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt alle anstehenden Klausuren an.
    !klausuren
    """
    klausurNamen = []
    klausurDaten = []
    klausurDauer = []
    klausurOrte = []
    with open(botData.modulesDirectory + "/data/klausuren/klausuren.txt") as fp: 
        lines = fp.readlines() 
        for line in lines: 
            if "#" in line:
                continue
            klausurNamen.append(line.split(" ")[0])
            klausurDaten.append(datetime.datetime(int(line.split(" ")[3]), int(line.split(" ")[2]), int(line.split(" ")[1]), int(line.split(" ")[4])))
            klausurDauer.append(int(line.split(" ")[5]))
            klausurOrte.append(line.split("\"")[1])
    
    klausurString = ":dizzy_face: Die anstehenden Klausuren sind\n"
    
    now = datetime.datetime.now()
    counter = 0
    
    maxLength = len(max(klausurNamen, key=len))
    
    for klausur in klausurNamen:
        if (klausurDaten[counter] - now).days >= 0:
            klausurString = klausurString + "```ml\n" + klausur 
            for i in range(0, (maxLength - len(klausur))):
                klausurString = klausurString + " " 
            klausurString = klausurString + " am " + klausurDaten[counter].strftime("%d.%m.%Y um %H:%M:%S") + " (in " + str((klausurDaten[counter] - now).days).zfill(2) + " Tagen!) 'Ort: \"" + klausurOrte[counter] + "\"```"

        counter = counter + 1
        
    
    klausurString = klausurString  
    await modules.bottiHelper._sendMessagePingAuthor(message, klausurString)

async def random(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl würfelt eine zufällige Zahl.
    !random {NUMBER}
    {NUMBER} Ganze Zahl > 0
    !random 1000
    """
    if str(message.content[8:]).isdigit() and str(message.content[8:]) != "":
        await modules.bottiHelper._sendMessagePingAuthor(message, ":game_die: Die Zufallszahl ist {0}!".format(randint(0, int(message.content[8:]))))
    else:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Bitte wähle eine obere Grenze!")

async def studispruch(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt einen Studispruch an.
    !studispruch
    """
    sprueche = [ 
        "Warst im Abi nicht so hell, Kragen hoch und BWL!",
        "Rosen sind rot,\nUni verpennt,\nGehalt kommt trotzdem,\nDualer Student.",
        "Die Haare lang, die Arme schmächtig - der studiert Elektrotechnik!",
        "Die Arme dünn, der Lörres schmächtig - der studiert Elektrotechnik!",
        "Alter Benz und Taxischein - das muss ein Philologe sein!",
        "Beim Dichten bin ich Spezialist - Hallo I bims, 1 Germanist!",
        "Noch nie von einer Frau besucht,\nInfo, 30, Jungfrau sucht.",
        "Papis Geld und große Namen, Jura kurz vorm Staatsexamen.",
        "Mandala-Kunst und Krankenschein - der muss Student auf Lehramt sein!",
        "Nächte wach, dank Ritalin - Ich studiere Medizin!",
        "Dreadlocks und Sozialkritik, BA-Student der Politik.",
        "Das Konto leer, doch ständig breit, ich hab studiert Sozialarbeit!",
        "1000 Männer, eine Frau - ich studier' Maschinenbau!",
        "Karohemd und Samenstau - der studiert Maschinenbau!",
        "Wer läuft so spät durch die Stadt und singt?\n\nEs ist der Student, vor Rausch fast blind.\n\nEr hält ihn sicher, er hält ihn warm,\nden Döner unter seinem Arm!",
        "Gelfrisur und Polohemd - der ist BWL-Student.",
        "Weil ich Freunde niemals hatte, studier' ich heut' auf Lehramt Mathe.",
        "Die Sonne lacht, die Leber brennt, ich lieg im Bett und bin Student.",
        "Burnout und ohne Energie, Patient und Student der Psychologie.",
        "Ene Mene Meise, die Klausur wird scheiße.",
        "Roses are red,\nviolets are blue.\nThere's always an asian,\nwho's better than you.",
        "Ein kurzes Gedicht:\n\nIch lerne\nnicht gerne.",
        "Wunderschön,\nin der Hose mächtig,\nich studier' Elektrotechnik!",
        "Zersaustes Haar und Blumenkleid, Studentin der Sozialarbeit.",
        "Trikot an, Klausur verpennt, das ist wohl ein Sportstudent.",
        "Wer sein Studium liebt, der schiebt!"
    ]
    
    zufallszahl = randint(0, len(sprueche) - 1)
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":scroll: Hier ist dein Spruch:\n{}\n".format(sprueche[zufallszahl]))

async def thisisfine(botti, message, botData):
    """ 
    Für alle ausführbar
    Bei diesem Befehl ist alles fine. Auch in animiert.
    !thisisfine {GIF}
    {GIF} "", "gif"
    !thisisfine\r!thisisfine gif
    """
    
    try:
        isGIFResquested = False
        if message.content.split(" ")[1].lower() == "gif":
            isGIFResquested = True
    except:
        pass
    
    numberOfDays = (datetime.datetime(2021, 3, 26, 9, 0, 0) - datetime.datetime.now()).days
    
    if not isGIFResquested:
        file = botData.modulesDirectory + "/data/images/temp/thisisfine_{}.jpg".format(str(numberOfDays))
        imageToEdit = Image.open(botData.modulesDirectory + "/data/images/thisisfine.jpg")
    else:
        file = botData.modulesDirectory + "/data/images/temp/thisisfine_{}.gif".format(str(numberOfDays))
        imageToEdit = Image.open(botData.modulesDirectory + "/data/images/thisisfine.gif")
    
    titleFont = ImageFont.truetype(botData.modulesDirectory + "/data/images/fonts/impact.ttf", 35) 

    imageString = "* ExPhyA in {} Tagen *".format(numberOfDays)  
    shadowcolor = "black"    
    fontColor = (255, 255, 255)    
    cacheString = ""
    if exists(file) == False:
        if not isGIFResquested:
            drawImage = ImageDraw.Draw(imageToEdit)
            x = 5
            y = 5
            
            drawImage.text((x-2, y-2), imageString, font=titleFont, fill=shadowcolor)
            drawImage.text((x+2, y-2), imageString, font=titleFont, fill=shadowcolor)
            drawImage.text((x-2, y+2), imageString, font=titleFont, fill=shadowcolor)
            drawImage.text((x+2, y+2), imageString, font=titleFont, fill=shadowcolor)
            
            drawImage.text((x, y), imageString, fontColor, font=titleFont)
            
            imageToEdit.save(file)
        else:
            frames = []
            for frame in ImageSequence.Iterator(imageToEdit):
                frame = frame.convert('RGBA')
                drawImage = ImageDraw.Draw(frame)
                x, y = drawImage.textsize(imageString)
                
                drawImage.text(((x/2)-2, (y/2)-2 + 10), imageString, font=titleFont, fill=shadowcolor)
                drawImage.text(((x/2)+2, (y/2)-2 + 10), imageString, font=titleFont, fill=shadowcolor)
                drawImage.text(((x/2)-2, (y/2)+2 + 10), imageString, font=titleFont, fill=shadowcolor)
                drawImage.text(((x/2)+2, (y/2)+2 + 10), imageString, font=titleFont, fill=shadowcolor)
            
                drawImage.text((x/2, y/2 + 10), imageString, fontColor, font=titleFont)
                
                del drawImage
                
                b = io.BytesIO()
                frame.save(b, format="GIF")
                frame = Image.open(b)
                frames.append(frame)

            frames[0].save(file, format="GIF", save_all=True, append_images=frames[1:])
    else:
        cacheString = " _(cached image)_"
    
    await message.channel.send(content = "{}{}".format(message.author.mention, cacheString), file = discord.File(file))

async def vorschlag(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl schickt einen Vorschlag an den Bot-Entwickler.
    !message {MESSAGE}
    {MESSAGE} String [Nachricht, die gesendet werden soll]
    !vorschlag Dies ist ein Test
    """
    if message.guild is not None:
        if botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel is None:
            await botti.get_user(ids.userIDs.ITZFLUBBY).create_dm()
        sentMessage = await botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel.send("**{0}#{1}** ({2}) hat auf **{3} ({4}) / {5} ({6})** folgendes geschrieben: _'{7}'_. | {8}".format(message.author.name, message.author.discriminator, message.author.id, message.guild.name, message.guild.id, message.channel.name, message.channel.id, str(message.content[9:]), modules.bottiHelper._getTimestamp()))
    else:
        sentMessage = await botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel.send("**{0}#{1}** ({2}) hat im Privat-Chat folgendes geschrieben: _'{3}'_. | {4}".format(message.author.name, message.author.discriminator, message.author.id, str(message.content[9:]), modules.bottiHelper._getTimestamp()))
    
    await sentMessage.add_reaction("✅")
    await sentMessage.add_reaction("💤")
    await sentMessage.add_reaction("❌")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":bookmark_tabs: Deine Nachricht wurde erfolgreich zugestellt!")