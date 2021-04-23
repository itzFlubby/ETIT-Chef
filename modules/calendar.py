import datetime
import discord
import modules.bottiHelper
import modules.data.ids as ids
import requests

from dateutil.tz import tzlocal
from icalendar import Calendar, vDatetime

def _appendItem(itemList, day, start, end, summary):
    itemList[day].append("`" + start.strftime("%H:%M") + " - " + end.strftime("%H:%M` ") + summary + "\n")
    
def _compareDate(first, second):
    if first.month < second.month or first.day < second.day :
        return 1

    if first.month > second.month or first.day > (second.day + 6): # 7 days in week -> 0, 1, 2, 3, 4, 5, 6 -> +6 to include all events in week
        return 2
        
    return 0
    
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

def _retrieveExams(botData, content):
    calendar = Calendar.from_ical(content)
    
    exams = []
    
    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.decoded("summary").decode("utf-8")
            if summary[:7] == "KLAUSUR": # Here is the '==' REQUIRED instead of 'is', because the value is being checked
                dtstart, dtend = _getTimeInCorrectTimezone(component)
                exams.append(component.decoded("summary").decode("utf-8")[10:].replace(" ", "_") + dtstart.strftime(" %d %m %Y %H 0 \"UNBEKANNT\"\n"))
                
    with open(botData.modulesDirectory + "data/klausuren/klausuren.txt", "w+") as f:
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
            "value": "kai"
        },
        "Informationstechnik": {
            "emoji": ":computer:",
            "value": "IT"
        }
    }
    
    for key in replacementDict:
        if key in summary:
            summary = "{emoji} {summary}".format(emoji = replacementDict[key]["emoji"], summary = summary.replace(key, replacementDict[key]["value"]))
    
    return summary
    
async def updatecalendar(botti, message, botData):
    """
    Für alle ausführbar
    Dieser Befehl aktualisiert den Kalender.
    !updatecalendar
    """
    request = requests.get(botData.calendarURL)
    with open(botData.modulesDirectory + "data/calendar/cal.ical", "w+") as f:
        f.write(request.text.replace("\r", ""))
        
    _retrieveExams(botData, request.text)
    
    await modules.bottiHelper._sendMessagePingAuthor(message, ":calendar: Der Kalender wurde aktualisiert!")

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
    
    content = ""
    with open(botData.modulesDirectory + "data/calendar/cal.ical", "r") as f:
        content += f.read()
        
    calendar = Calendar.from_ical(content)

    weekdayItems = [[], [], [], [], [], [], []]
    startOfWeek = now - datetime.timedelta(days = now.weekday())
    
    lastModified = 0
    
    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = _shortenSummary(component.decoded("summary").decode("utf-8"))
            dtstart, dtend = _getTimeInCorrectTimezone(component)
                
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
                    if (abs(startOfWeek.isocalendar()[1] - dtstart.isocalendar()[1]) % rrule["INTERVAL"][0]) is 0:
                        _appendItem(weekdayItems, dtstart.weekday(), dtstart, dtend, summary)
                    continue
                    
                if "BYDAY" in rrule:
                    if len(rrule["BYDAY"]) > 1:
                        for i in range(len(rrule["BYDAY"])):
                            appendDate = True
                            weekdayIndex = { "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6 }
                            indexDay = weekdayIndex[rrule["BYDAY"][i]]
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
                            if (vDDDType.dt - startOfWeek).days < 7: # < 7 : If event is in this week (7 days in week)
                                returnToMainloop = True
                                break
                    else:   
                        for exdate in component.decoded("exdate"):
                            for vDDDType in exdate.dts:
                                if (vDDDType.dt - startOfWeek).days < 7: # < 7 : If event is in this week (7 days in week)
                                    returnToMainloop = True
                                    break
                    
                    if not returnToMainloop:
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
                
        data.add_field(name = weekdayNames[i] + (startOfWeek + datetime.timedelta(days = i)).strftime(" `(%d.%m.%Y)`"), value = dayString if dayString is not "" else "-", inline = False)
    
    data.set_author(name = "🗓️ Wochenplan für ETIT")
    data.set_thumbnail(url = botti.user.avatar_url)
    data.set_footer(text = "Vorlesung, wenn nicht anderweitig angegeben.\nJegliche Angaben ohne Gewähr.\nStand: {}".format(modules.bottiHelper._toGermanTimestamp(lastModified)))
    
    await modules.bottiHelper._sendEmbed(message, "{}".format(message.author.mention), embed = data)