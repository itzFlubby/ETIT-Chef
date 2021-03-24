import discord
import modules.bottiHelper
import os
import xlrd
import xlwt

from xlutils.copy import copy

async def polls(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl listet alle aktiven Umfragen auf.
    !polls
    """
    await modules.bottiHelper._sendMessage(message, ":grey_question: Es gibt die folgenden Umfragen {}:".format(message.author.mention))
    all_polls = "```\n"
    for filename in os.listdir(botData.modulesDirectory + "/data/polls"):
        all_polls += filename.split(".")[0] + "\n";
    await modules.bottiHelper._sendMessage(message, all_polls + "```")

async def viewpoll(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl listet alle Abstimmungsmöglichkeiten einer Umfrage auf.
    !viewpoll {UMFRAGE}
    {UMFRAGE} String [Umfragen-Name kann mit !polls angezeigt werden]
    !viewpoll Umfrage
    """
    try:
        pollname = message.content.split(" ")[1].lower()
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!viewpoll"))      
        return
    try:
        workbook = xlrd.open_workbook(botData.modulesDirectory + "/data/polls/" + pollname + ".xls")
    except FileNotFoundError:
        
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Diese Umfrage existiert nicht! Verwende `!polls`, um die aktuellen Abstimmungen anzuzeigen.")
        return
    sheet = workbook.sheet_by_index(0)
    
    await modules.bottiHelper._sendMessage(message, ":grey_question: Für die Umfrage `" + pollname + "` stehen die folgenen Abstimmungsmöglichkeiten zur Verfügung {}:".format(message.author.mention))
    all_options = "```\n"
    for i in range(2, sheet.ncols):
        try:
            content = sheet.cell_value(rowx=2, colx=i)
            if content == "":
                break
        except IndexError:
            break
        all_options += content + "\n"
    await modules.bottiHelper._sendMessage(message, all_options + "```")
    
async def vote(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl stimmt in einer Umfrage ab.
    !vote {UMFRAGE} {OPTION}
    {UMFRAGE} String [Name der Umfrage; Umfragen können mit !polls gelistet werden]
    {OPTION} String [Optionen können mit !viewpoll {UMFRAGE} aufgelistet werden]
    !vote Umfrage Option
    """
    try:
        pollname = message.content[6:].split(" ")[0].lower()
        polloption = message.content.split(" ")[2].lower()
    except IndexError:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams("!vote"))      
        return
    try:
        workbook = xlrd.open_workbook(botData.modulesDirectory + "/data/polls/" + pollname + ".xls")
    except FileNotFoundError:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Die Umfrage `{0}` existiert nicht! Verwende `!polls`, um die aktuellen Abstimmungen anzuzeigen.".format(pollname))
        return
    old_sheet = workbook.sheet_by_index(0)
    wb = copy(workbook)
    new_sheet = wb.get_sheet(0)
    voted = False
    for i in range(2, old_sheet.ncols):
        content = old_sheet.cell_value(rowx=2, colx=i)
        if content == polloption:
            new_sheet.write(old_sheet.nrows, i, "X")
            voted = True
            break
    if voted is False:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Die Option **{0}** existiert in dieser Umfrage nicht!".format(polloption))
        return
    new_sheet.write(old_sheet.nrows, 0, message.author.name + "#" + message.author.discriminator)
    new_sheet.write(old_sheet.nrows, 1, "")
    wb.save(botData.modulesDirectory + "/data/polls/" + pollname + ".xls")
    await modules.bottiHelper._sendMessagePingAuthor(message, ":grey_question: Du hast in der Umfrage `{0}` erfolgreich für **{1}** abgestimmt.".format(pollname, polloption))
 