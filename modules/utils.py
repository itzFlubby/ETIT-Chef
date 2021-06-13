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
import modules.timer
import modules.utils

from os.path import exists
from PIL import Image, ImageFont, ImageDraw, ImageSequence 
from random import choice
from random import randint

def _getFormattedCommands(module, botData):
    formattedCommands = []
    longestCommandLength = len(max(module.commandNameList, key = len)) + 1
    
    tempFormattedString = ""
    for command in module.commandNameList:
        commandLength = len(command)
        infoText = getattr(module.module, command).__doc__
        if not infoText:
            infoText = "<NONE>\n<NONE>\n<NONE>\n<NONE>\n"
        infoTextLines = infoText.replace("    ", "").replace("Dieser Befehl ", "...").split("\n")
        
        formattedCommand = "`" + botData.botPrefix + command + " " * (longestCommandLength - commandLength) + infoTextLines[2] + "`\n"
        if(len(tempFormattedString + formattedCommand) > 1024):
            formattedCommands.append(tempFormattedString)
            tempFormattedString = ""
        tempFormattedString += formattedCommand
    formattedCommands.append(tempFormattedString)    
    return formattedCommands
  
async def _updateHelpEmbed(message, moduleIndex, moduleList, botData):
    embed = message.embeds[0]
    embed.clear_fields()
    
    formattedCommands = _getFormattedCommands(moduleList[moduleIndex], botData)
    for commandSection in formattedCommands:
        embed.add_field(name = "⠀", value = commandSection, inline = False)
    embed.set_footer(text = "Ausgewähles Modul: {module}\nIn diesem befinden sich {moduleCommands} Befehle!".format(module = moduleList[moduleIndex].moduleName, moduleCommands = len(moduleList[moduleIndex].commandNameList)))
    
    view = discord.ui.View(timeout = None)
    for run, module in enumerate(moduleList):
        buttonStyle = discord.ButtonStyle.secondary if run != moduleIndex else discord.ButtonStyle.success
        view.add_item(discord.ui.Button(style = buttonStyle, emoji = module.emoji, label = module.moduleName, custom_id = str(run)))
    
    await message.edit(embed = embed, view = view)

async def antwortaufalles(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt dir die Antwort auf alles an.
    !antwortaufalles
    """
    await modules.bottiHelper._sendMessagePingAuthor(message, ":milky_way: Die Antwort auf die Frage nach dem Leben, dem Universum und dem ganzen Rest ist :four::two:!")

async def bullshit(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl hat noch nie so einen riesigen Haufen Scheiße gesehen...
    !bullshit
    """
    file = botData.modulesDirectory + "data/images/temp/bullshit_{}.png".format(message.author.id)
    
    titleFont = ImageFont.truetype(botData.modulesDirectory + "data/images/fonts/Tahoma.ttf", 31) 
    
    imageString = message.author.nick if not (message.author.nick is None) else message.author.name
    fontColor = (247, 233, 26)    
    cacheString = ""
    if not (exists(file)):
        imageToEdit = Image.open(botData.modulesDirectory + "data/images/bullshit.png").convert('RGB') 
        drawImage = ImageDraw.Draw(imageToEdit)
        
        drawImage.text((10, 345), imageString, fontColor, font = titleFont)
        
        imageToEdit.save(file)
        
    else:
        cacheString = " _(cached image)_"
    
    await message.channel.send(content = "{}{}".format(message.author.mention, cacheString), file = discord.File(file))

async def checkthepins(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl... schau bitte einfach in die Pins.
    !checkthepins {@USER}
    {@USER} <leer>, Nutzer-Erwähnung
    !checkthepins\r!checkthepins @ETIT-Chef
    """
    user = message.author if len(message.mentions) == 0 else message.mentions[0]
        
    
    with open(botData.modulesDirectory + "data/images/checkthepins.gif", "rb") as f:
        await modules.bottiHelper._sendMessage(message = message, content = user.mention, file = discord.File(f))

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
        subcommand = message.content.split(" ")[1]
        commandName = subcommand if (subcommand[0] is not botData.botPrefix) else subcommand[1:]
    except:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "command"))      
        return
        
    infoText = ""
    
    for module in botData.allCommandModules:
        if commandName in module.commandNameList:
            infoText = getattr(module.module, commandName).__doc__
            break
    
    if infoText in [ None, "" ]:
        infoText = "\n\nDieser Befehl existiert nicht, oder es ist keine Hilfe verfügbar!\nAusführung nicht verfügbar.\n"
    
    infoTextLines = infoText.replace("    ", "").split("\n")
    del(infoTextLines[0])
    del(infoTextLines[-1])
    
    data = discord.Embed(
        title = botData.botPrefix + commandName,
        color = 0x009AFF,
        description = ""
    )
    data.set_author(name = "❓ Befehls-Hilfe") 
    data.set_thumbnail(url = botti.user.avatar.url)    
    data.set_footer(text = infoTextLines[0])
    
    data.add_field(name = "Beschreibung", value = infoTextLines[1] + "\n⠀", inline = False)
    data.add_field(name = "Ausführung", value = infoTextLines[2] + "\n⠀", inline = False)
    
    for i in range(3, len(infoTextLines)):
        if infoTextLines[i][0] == "{":
            commandParameters = infoTextLines[i].split("}")
            data.add_field(name = "Gültige Werte für " + commandParameters[0] + "}", value = commandParameters[1].replace("\r", "\n") + "\n⠀", inline = False)
        else:
            data.add_field(name = "Beispiel", value = infoTextLines[i].replace("\r", "\n") + "\n⠀", inline = False)
    
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

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
    moduleList = botData.allCommandModules.copy()
    
    data = discord.Embed(
        title = ":question: Befehls-Hilfe",
        color = 0x009AFF,
        description = "Klicke unten auf die Knöpfe, um die Befehle aus den jeweiligen Modulen anzuzeigen!"
    )
    data.set_thumbnail(url = botti.user.avatar.url)
    
    DM = await modules.bottiHelper._createDM(botti, message.author.id)
    messageInDM = await DM.send(embed = data)
    await _updateHelpEmbed(messageInDM, 0, moduleList, botData)
    
    messageInChannel = await modules.bottiHelper._sendMessagePingAuthor(message, content = ":question: Hier ist eine Befehls-Hilfe! Diese wurde dir außerdem im Privat-Chat geschickt!", embed = data)
    await _updateHelpEmbed(messageInChannel, 0, moduleList, botData)
        
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
    data.set_thumbnail(url = message.guild.icon.url)
            
    invites = await message.guild.invites()
    
    for invite in invites:
        if invite.max_age == 0:
            data.add_field(name = "Permanent-Link", value = invite.url)
            data.set_footer(text = "Verwendungen: {0}\nErsteller: {1}#{2}".format(str(invite.uses), invite.inviter.name, str(invite.inviter.discriminator)))  
            await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)
            return
    
    invite = await message.channel.create_invite(max_age = 3600, unique = False, reason = "Requested by User.")       
    data.add_field(name = "Temporär-Link", value = invite.url)
    data.set_footer(text = "Gültigkeit: Eine Stunde\nErsteller: {0}#{1}".format(invite.inviter.name, str(invite.inviter.discriminator)))  
    await modules.bottiHelper._sendMessagePingAuthor(message = message, embed = data)

async def kekse(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl... nunja... Kekse sind einfach toll!
    !kekse
    """
    botMessage = await modules.bottiHelper._sendMessage(message, "**Ich mag** :cookie::cookie::cookie: **OMNOMNOM**")
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.NEIN))
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.DOCH))
    await botMessage.add_reaction(modules.construct._constructEmojiStringNoBracket(ids.emojiIDs.OH))
    await botMessage.add_reaction("🍪")

async def our(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl ist unser Befehl!
    !our {PROPERTY}
    {PROPERTY} [String]
    !our bread
    """    
    if len(message.content.split(" ")) < 2:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "our"))
        return
    
    imageString = "Our " + message.content[5:] # 5 = len("!our ")
    file = botData.modulesDirectory + "data/images/temp/bugs_bunny_our_{}.png".format(imageString.replace(" ", "_"))
    
    titleFont = ImageFont.truetype(botData.modulesDirectory + "data/images/fonts/impact.ttf", 42) 
    
    fontColor = (224, 212, 64)    
    shadowcolor = (0, 0, 0)
    cacheString = ""
    if not (exists(file)):
        imageToEdit = Image.open(botData.modulesDirectory + "data/images/bugs_bunny_our.jpg").convert('RGB') 
        drawImage = ImageDraw.Draw(imageToEdit)
        x = 362 - int(titleFont.getsize(imageString)[0] / 2)
        y = 345
        drawImage.text((x-2, y-2), imageString, font = titleFont, fill = shadowcolor)
        drawImage.text((x+2, y-2), imageString, font = titleFont, fill = shadowcolor)
        drawImage.text((x-2, y+2), imageString, font = titleFont, fill = shadowcolor)
        drawImage.text((x+2, y+2), imageString, font = titleFont, fill = shadowcolor)
        drawImage.text((x, y), imageString, fontColor, font = titleFont)
        
        imageToEdit.save(file)
        
    else:
        cacheString = " _(cached image)_"
    
    await message.channel.send(content = "{}{}".format(message.author.mention, cacheString), file = discord.File(file))
          
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
    
    numberOfDays = (datetime.datetime(2021, 8, 9, 0, 0, 0) - datetime.datetime.now()).days
    
    if not isGIFResquested:
        file = botData.modulesDirectory + "/data/images/temp/thisisfine_{}.jpg".format(str(numberOfDays))
        imageToEdit = Image.open(botData.modulesDirectory + "/data/images/thisisfine.jpg")
    else:
        file = botData.modulesDirectory + "/data/images/temp/thisisfine_{}.gif".format(str(numberOfDays))
        imageToEdit = Image.open(botData.modulesDirectory + "/data/images/thisisfine.gif")
    
    titleFont = ImageFont.truetype(botData.modulesDirectory + "/data/images/fonts/impact.ttf", 35) 

    imageString = "* KAI in {} Tagen *".format(numberOfDays)  
    shadowcolor = "black"    
    fontColor = (255, 255, 255)    
    cacheString = ""
    if not exists(file):
        if not isGIFResquested:
            drawImage = ImageDraw.Draw(imageToEdit)
            x = 192 - int(titleFont.getsize(imageString)[0] / 2)
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
                x, y = titleFont.getsize(imageString)
                
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
    userDM = await modules.bottiHelper._createDM(botti, ids.userIDs.ITZFLUBBY)
    sentMessage = await userDM.send("**{author.name}#{author.discriminator}** ({author.id}) hat im **{guild.name} ({guild.id}) / {channel.name} ({channel.id})** folgendes geschrieben: _'{content}'_. | {timestamp}".format(author = message.author, guild = message.guild, channel = message.channel, content = message.content[11:], timestamp = modules.bottiHelper._getTimestamp()))

    await sentMessage.add_reaction("✅")
    await sentMessage.add_reaction("💤")
    await sentMessage.add_reaction("❌")
    await sentMessage.add_reaction("👑")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":bookmark_tabs: Deine Nachricht wurde erfolgreich zugestellt!")