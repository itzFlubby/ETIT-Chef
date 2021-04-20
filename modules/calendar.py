import datetime
import discord
import modules.bottiHelper
import modules.data.ids as ids
import requests

from icalendar import Calendar, vDatetime

def _appendItem(itemList, day, start, end, summary):
    itemList[day].append("`" + start.strftime("%H:%M") + " - " + end.strftime("%H:%M` ") + summary + "\n")
    
def _compareDate(first, second):
    if first.month < second.month or first.day < second.day :
        return 1

    if first.month > second.month or first.day > (second.day + 6):
        return 2
        
    return 0
    
def _retrieveExams(botData, content):
    calendar = Calendar.from_ical(content)
    
    exams = []
    
    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.decoded("summary").decode("utf-8")
            if summary[:7] == "KLAUSUR": # Here is the '==' REQUIRED instead of 'is', because the value is being checked
                dtstart = component.decoded("dtstart")
                dtend = component.decoded("dtend")
                if component.content_line("dtend", dtend)[-6:] == "+00:00":
                    dtstart += datetime.timedelta(hours = 2)
                
                exams.append(component.decoded("summary").decode("utf-8")[10:].replace(" ", "_") + dtstart.strftime(" %d %m %Y %H 0 \"UNBEKANNT\"\n"))
                
    with open(botData.modulesDirectory + "data/klausuren/klausuren.txt", "w+") as f:
        for exam in exams:
            f.write(exam)
    
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