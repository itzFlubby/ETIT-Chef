import datetime
import discord
import modules.bottiHelper
import modules.data.ids as ids
import requests

from dateutil.tz import tzlocal
from icalendar import Calendar, vDatetime
from os.path import exists

class Exam:
    def __init__(self, pName, pDate, pDuration, pLocation):
        self.name = pName
        self.date = pDate
        self.duration = pDuration
        self.location = pLocation

def _appendItem(itemList, day, start, end, summary):
    itemList[day].append("`" + start.strftime("%H:%M") + " - " + end.strftime("%H:%M` ") + summary + "\n")
    
def _compareDate(first, second):
    if first.month < second.month or first.day < second.day :
        return 1

    if first.month > second.month or first.day > (second.day + 6): # 7 days in week -> 0, 1, 2, 3, 4, 5, 6 -> +6 to include all events in week
        return 2
        
    return 0
    
def _dateNotExcluded(component, startDate, checkRange):
    if "exdate" in component:
        if hasattr(component.decoded("exdate"), "dts"):
            for vDDDType in component.decoded("exdate").dts:
                if (vDDDType.dt - startDate).days in checkRange:
                    return False
        else:   
            for exdate in component.decoded("exdate"):
                for vDDDType in exdate.dts:
                    if (vDDDType.dt.date() - startDate.date()).days in checkRange:
                        return False
    return True

def _displayToUser(userRoleNames, name):
    if name not in userRoleNames:
        return False

    return True
        
def _extractLink(component):
    description = component.decoded("description").decode("utf-8")
    if "</a>" in description:
        return description.split("\"")[1]
    return description
        
def _getCourseAndSemester(message):
    buildInfo = ""
    if "ETIT" in message.channel.category.name:
        buildInfo += "ETIT_SEM_"
    elif "MIT" in message.channel.category.name:
        buildInfo += "MIT_SEM_"
    else:
        return None
        
    try:
        sem = message.channel.category.name[0]
        return buildInfo + sem
    except:
        return None
    
def _getCurrentTime():
    return datetime.datetime.now(tzlocal())
   
def _getTimeInCorrectTimezone(component):
    dtstart = component.decoded("dtstart")
    dtend = component.decoded("dtend")
    if component.content_line("dtend", dtend)[-6:] == "+00:00": # If timezone is UTC
        dtstart += datetime.timedelta(hours = _getUTCOffset())
        dtend += datetime.timedelta(hours = _getUTCOffset())
        
    return dtstart, dtend
   
def _getUTCOffset():
    return int(datetime.datetime.now(tzlocal()).utcoffset().seconds / 3600)

def _hasLinkEmbedded(component):
    if "description" in component:
        return "zoom" in component.decoded("description").decode("utf-8").lower()
    return False

def _retrieveExams(botData, courseAndSemester):
    content = ""
    with open(botData.modulesDirectory + "data/calendar/" + courseAndSemester + ".ical", "r") as f:
        content += f.read()
        
    calendar = Calendar.from_ical(content)
    
    exams = []
    
    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.decoded("summary").decode("utf-8")
            if summary[:7] == "KLAUSUR": # Here is the '==' REQUIRED instead of 'is', because the value is being checked
                dtstart, dtend = _getTimeInCorrectTimezone(component)
                location = component.decoded("location").decode("utf-8")
                location = "UNBEKANNT" if (location == "") else location
                    
                exams.append(component.decoded("summary").decode("utf-8")[10:] + dtstart.strftime(",%d,%m,%Y,%H,0,\"" + location + "\"\n"))
                
    with open(botData.modulesDirectory + "data/klausuren/" + courseAndSemester + ".txt", "w+") as f:
        for exam in exams:
            f.write(exam)

def _shortenSummary(summary):
    replacementDict = {
        "Höhere Mathematik": {
            "emoji": ":chart_with_upwards_trend:",
            "value": "HM"
        },
        "Inverted Classroom": {
            "emoji": "",
            "value": "IC"
        },
        "Elektronische Schaltungen": {
            "emoji": ":radio:",
            "value": "ES"
        },
        "Elektromagnetische Felder": {
            "emoji": ":magnet:",
            "value": "EMF"
        },
        "Komplexe Analysis und Integraltransformationen": {
            "emoji": ":triangular_ruler:",
            "value": "KAI"
        },
        "Informationstechnik": {
            "emoji": ":computer:",
            "value": "IT"
        },
        "Optik und Festkörperelektronik": {
            "emoji": ":eyes:",
            "value": "OFE"
        },
        "Grundlagen der Hochfrequenztechnik": {
            "emoji": ":satellite:",
            "value": "GHF"
        },
        "Maschinenkonstruktionslehre": {
            "emoji": ":gear:",
            "value": "MKL"
        },
        "Technische Mechanik": {
            "emoji": ":wrench:",
            "value": "TM"
        },
        "Elektroenergiesysteme": {
            "emoji": ":battery:",
            "value": "EES"
        }
    }
    
    for key in replacementDict:
        if key in summary:
            summary = "{emoji} {summary}".format(emoji = replacementDict[key]["emoji"], summary = summary.replace(key, replacementDict[key]["value"]))
    
    return summary

def _updateAll(botData):
    content = ""
    for courseAndSemester in botData.calendarURLs.keys():
        calendarFile = botData.modulesDirectory + "data/calendar/" + courseAndSemester + ".ical"
        if exists(calendarFile):
            
            with open(calendarFile, "r") as f:
                calendarContents = f.read()
                content += calendarContents[calendarContents.find("BEGIN:VEVENT"):].split("END:VCALENDAR")[0]
    
    with open(botData.modulesDirectory + "data/calendar/scheme.txt", "r") as f:
        scheme = f.read().split("#")
    
    with open(botData.modulesDirectory + "data/calendar/all.ical", "w+") as f:
        f.write(scheme[0] + content.replace("\r", "") + scheme[1])               

async def klausuren(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt alle anstehenden Klausuren an.
    !klausuren
    """
    exams = []
    
    courseAndSemester = _getCourseAndSemester(message)
    
    if "slash" in message.content:
        courseAndSemester = "all"
        userRoleNames = [ role.name for role in message.author.roles ]
        
    if courseAndSemester == None:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":calendar: Dein Semester und Studiengang wurde nicht erkannt. Verwende den Befehl in einem Text-Kanal von deinem Semester!")    
        return
    
    umlautCharmap = { ord("ä"): "ae", ord("ü"): "ue", ord("ö"): "oe", ord("ß"): "ss" }
    
    with open(botData.modulesDirectory + "/data/klausuren/" + courseAndSemester + ".txt") as fp: 
        lines = fp.readlines() 
        for line in lines: 
            if "#" in line:
                continue
            
            contents = line.split(",")  
            if "slash" in message.content:
                if not _displayToUser(userRoleNames, contents[0]):
                    continue
              
            exams.append(Exam(  pName = contents[0].translate(umlautCharmap), 
                                pDate = datetime.datetime(int(contents[3]), int(contents[2]), int(contents[1]), int(contents[4])),
                                pDuration = int(contents[5]),
                                pLocation = line.split("\"")[1] 
                            ))
    
    if len(exams) == 0:
        examString = "```Gerade sind keine anstehenden Klausuren vermerkt!```"
    else:
        now = datetime.datetime.now()
        exams = sorted(exams, key = lambda exam: (exam.date - now).days)
        
        maxLength = len(max([exam.name for exam in exams], key = len))
        
        examString = ":dizzy_face: Die anstehenden Klausuren sind\n"
        for exam in exams:
            if (exam.date - now).days >= 0: # If Exam not in past
                examString += "```ml\n" + exam.name
                examString += " " * (maxLength - len(exam.name))
                examString += " am {date} (in {days} Tagen!) 'Ort: \"{location}\"```".format(date = modules.bottiHelper._toGermanTimestamp(exam.date), days = str((exam.date - now).days).zfill(2), location = exam.location)
    
    examString += "Jegliche Angaben ohne Gewähr."   
    if not "slash" in message.content:
        await modules.bottiHelper._sendMessagePingAuthor(message, examString)
    else:
        return examString # Return examString to slash-command-handler to send hidden message
        
async def updatecalendar(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl aktualisiert den Kalender.
    !updatecalendar
    """
    courseAndSemester = _getCourseAndSemester(message)
    
    if courseAndSemester == None:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":calendar: Semester und Studiengang wurde nicht erkannt. Verwende den Befehl in einem Text-Kanal von dem Semester, dessen Kalender aktualisiert werden soll!")    
        return
    
    if botData.calendarURLs[courseAndSemester] == None:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":calendar: Für dieses Semester gibt es in diesem Studiengang noch kein Kalender!")    
        return
    
    request = requests.get(botData.calendarURLs[courseAndSemester])
    with open(botData.modulesDirectory + "data/calendar/" + courseAndSemester + ".ical", "w+") as f:
        f.write(request.text.replace("\r", ""))
        
    
    _retrieveExams(botData, courseAndSemester)
    
    _updateAll(botData)
    _retrieveExams(botData, "all")
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":calendar: Der Kalender für `{courseAndSemester}` wurde aktualisiert!".format(courseAndSemester = courseAndSemester))    

async def wochenplan(botti, message, botData):
    """ 
    Für alle ausführbar
    Dieser Befehl zeigt den Wochenplan an.
    !wochenplan {DATUM}
    {DATUM} <leer>, TT.MM.JJJJ
    !wochenplan\r!wochenplan 05.05.2021
    """

    now = datetime.datetime.now(tzlocal())
    if len(message.content) > 12: # 12 : len("!wochenplan ")
        try:
            date = message.content.split(" ")[1]
            items = date.split(".")
            now = datetime.datetime(int(items[2]), int(items[1]), int(items[0]), 0, 0, 0, tzinfo = datetime.timezone.utc)
        except:
            await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "wochenplan"))      
            return         
    
    courseAndSemester = _getCourseAndSemester(message)
    
    if "slash" in message.content:
        courseAndSemester = "all"
        userRoleNames = [ role.name for role in message.author.roles ]
        
    if courseAndSemester == None:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":calendar: Dein Semester und Studiengang wurde nicht erkannt. Verwende den Befehl in einem Text-Kanal von deinem Semester, oder benutze `/wochenplan` um einen personalisierten Kalender zu erhalten!")    
        return
        
    content = ""
    with open(botData.modulesDirectory + "data/calendar/" + courseAndSemester + ".ical", "r") as f:
        content += f.read()
        
    calendar = Calendar.from_ical(content)

    weekdayItems = [[], [], [], [], [], [], []]
    startOfWeek = now - datetime.timedelta(days = now.weekday())
    
    lastModified = 0
    
    for component in calendar.walk():
        if component.name == "VEVENT":
            decodedSummary = component.decoded("summary").decode("utf-8")
            if "slash" in message.content:
                try:    
                    if not _displayToUser(userRoleNames, decodedSummary.split(" - ")[1].split(" (")[0]):
                        continue
                except: # If somebody fucked up naming-scheme
                    continue
            summary = _shortenSummary(decodedSummary)
            dtstart, dtend = _getTimeInCorrectTimezone(component)
            
            if _hasLinkEmbedded(component):
                summary = "{summary} [[Zoom-Link]({link})]".format(summary = summary, link = _extractLink(component))
                
            if not lastModified:
                lastModified = component.decoded("last-modified")
            
            if "rrule" in component:
                rrule = component.decoded("rrule")
            
                if (dtstart - startOfWeek).days > 6: # 7 days in week -> 0, 1, 2, 3, 4, 5, 6 -> +6 to include all events in week
                    continue
                
                if "UNTIL" in rrule:
                    if (rrule["UNTIL"][0] - now).days < 0: # < 0 : If event is in the past
                        continue
                        
                if "COUNT" in rrule:
                    intervalModifier = rrule["INTERVAL"][0] if ("INTERVAL" in rrule) else 1
                    if (dtstart + datetime.timedelta(days = (7 * intervalModifier * rrule["COUNT"][0])) - now).days < 0: # < 0 : if event is in the past
                        continue
                
                if "INTERVAL" in rrule:
                    if (abs(startOfWeek.isocalendar()[1] - dtstart.isocalendar()[1]) % rrule["INTERVAL"][0]) is 0: # If interval event in this week
                        if _dateNotExcluded(component, startOfWeek, range(0, 7)):
                            _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                    continue
                    
                if "BYDAY" in rrule:
                    if len(rrule["BYDAY"]) > 1:
                        for byday in rrule["BYDAY"]:
                            appendDate = True
                            weekdayIndex = { "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6 }
                            indexDay = weekdayIndex[byday]
                            datetimeDay = startOfWeek + datetime.timedelta(days = indexDay)

                            if _dateNotExcluded(component, datetimeDay, range(0, 1)):
                                if (datetimeDay - dtend).days >= -1:
                                    _appendItem(weekdayItems, indexDay, dtstart, dtend, summary)
                            continue
                        
                if "exdate" in component:
                    if _dateNotExcluded(component, startOfWeek, range(0, 7)): # range(0, 7) : If event is in this week (7 days in week)
                        _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                    continue
                    
                _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                continue    
                
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
            
        if not dayString:
            continue
        data.add_field(name = weekdayNames[i] + (startOfWeek + datetime.timedelta(days = i)).strftime(" `(%d.%m.%Y)`"), value = dayString[:1024], inline = False)
    
    data.set_author(name = "🗓️ Wochenplan für " + (courseAndSemester if (courseAndSemester != "all") else message.author.name))
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Vorlesung, wenn nicht anderweitig angegeben.\nJegliche Angaben ohne Gewähr.\nStand: {}".format(modules.bottiHelper._toGermanTimestamp(lastModified)))
    
    if not "slash" in message.content:
        await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)
    else:
        return data # Return data to slash-command-handler to send hidden message