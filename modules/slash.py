import modules.bottiHelper
import modules.data.ids as ids
import modules.info
import modules.lerngruppe
import modules.mensa
import modules.utils
import traceback

from __main__ import botti, slash

from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.utils import manage_commands

from modules.data.botData import botData

@slash.slash(name="convert", description="Konvertiert einen Inhalt.", options = [ manage_commands.create_option(
    name = "typ",
    description = "Hier kannst du auswählen, wonach dein Inhalt konvertiert werden soll.",
    option_type = 3,
    choices = [ {
            "name": "Text zu Binär", 
            "value": "text bin"
        }, {
            "name": "Binär zu Text", 
            "value": "bin text"
        }, {
            "name": "Text zu Hex", 
            "value": "text hex"
        }, {
            "name": "Hex zu Text", 
            "value": "hex text"
        }, {
            "name": "Binär zu Hex", 
            "value": "bin hex"
        }, {
            "name": "Hex zu Binär", 
            "value": "hex bin"
        } ],
    required = True ),
    manage_commands.create_option(
    name = "inhalt",
    description = "Inhalt zum Konvertieren.",
    option_type = 3,
    required = True )])
async def _convert(ctx, typ, inhalt):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "!convert " + typ + " " + inhalt)
    await ctx.send(content = "Slash-Command: Convert")
    await modules.utils.convert(botti, msg, botData)

@slash.slash(name="klausuren", description="Zeigt die anstehenden Klausuren an.")
async def _klausuren(ctx: SlashContext):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    await ctx.send(content = "Slash-Command: Klausuren")   
    await modules.utils.klausuren(botti, msg, botData)    

@slash.slash(name="mensa", description="Zeigt den Speiseplan an.", options = [ manage_commands.create_option(
    name = "mensa",
    description = "Optional kannst du hier eine Mensa auswählen. Standard: Mensa am Adenauerring.",
    option_type = 3,
    choices = [ {
            "name": "Am Adenauerring", 
            "value": "adenauerring"
        }, {
            "name": "Erzbergstraße", 
            "value": "erzberger"
        }, {
            "name": "Schloss Gottesaue", 
            "value": "gottesaue"
        }, {
            "name": "Tiefbronner Straße", 
            "value": "tiefenbronner"
        }, {
            "name": "Caféteria Moltkestraße 30",
            "value": "x1moltkestrasse"
    } ],
    required = False ),
    manage_commands.create_option(
    name = "wochentag",
    description = "Optional kannst du hier den gewünschten Wochentag angeben. Standard: Morgen.",
    option_type = 3,
    choices = [ {
            "name": "Montag", 
            "value": "mo"
        }, {
            "name": "Dienstag", 
            "value": "di"
        }, {
            "name": "Mittwoch", 
            "value": "mi"
        }, {
            "name": "Donnerstag", 
            "value": "do"
        }, {
            "name": "Freitag", 
            "value": "fr"
        } ],
    required = False )])
async def _mensa(ctx, mensa = "adenauerring", wochentag = "none"):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    commandArgs = "!mensa " + mensa + " "
    if wochentag != "none":
        commandArgs = commandArgs + wochentag
    
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, commandArgs)
    await ctx.send(content = "Slash-Command: Mensa")
    await modules.mensa.mensa(botti, msg, botData)

@slash.slash(name="ping", description="Gibt die Discord-WebSocket-Latenz an.")
async def _ping(ctx: SlashContext):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    await ctx.send(content = ":satellite: Die Discord WebSocket-Protokoll-Latenz liegt bei **{0}ms**!".format(str(round((botti.latency * 1000), 2))), hidden = True) 

@slash.slash(name="templerngruppe", description="Erstellt oder verwaltet eine temporäre Lerngruppe", options = [ manage_commands.create_option(
    name = "option",
    description = "Optional kannst du hier Verwaltungbefehle eingeben.",
    option_type = 3,
    choices = [ {
            "name": "add", 
            "value": "add"
        }, {
            "name": "delete", 
            "value": "delete"
        }],
    required = False ),
    manage_commands.create_option(
    name = "user",
    description = "Optional kannst du hier einen Nutzer zum Hinzufügen angeben.",
    option_type = 6,
    required = False )])
async def _templerngruppe(ctx: SlashContext, option = "", user = None):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    commandArgs = " "
    if option == "":
        commandArgs = ""
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "!templerngruppe" + commandArgs + option)
    if user != "":
        msg.mentions = [ user ]
    await ctx.send(content = "Slash-Command: Templerngruppe")
    await modules.lerngruppe.templerngruppe(botti, msg, botData)

@slash.slash(name="test", description="Überprüft, ob einfach alles funzt...")
async def _test(ctx: SlashContext):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    await ctx.send(content = ":globe_with_meridians: Der Bot ist online und läuft ordnungsgemäß!", hidden = True) 

@slash.slash(name="userinfo", description="Zeigt Informationen über einen Benutzer an!", options = [ manage_commands.create_option(
    name = "benutzer",
    description = "Hier musst du einen Benutzer auswählen.",
    option_type = 6,
    required = True )])
async def _userinfo(ctx, benutzer):
    modules.bottiHelper._logSlashCommand(ctx, botData)
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    msg.mentions = [ benutzer ]
    await ctx.send(content = "Slash-Command: Userinfo")
    await modules.info.userinfo(botti, msg, botData)

@slash.slash(name="vorschlag", description="Sag mir deine Meinung! Gebe Verbesserungsvorschläge, oder -ideen ab!", options = [ manage_commands.create_option(
    name = "nachricht",
    description = "Hier kannst du deine Meinung reinschreiben. Bitte sei nicht zu böse :) !",
    option_type = 3,
    required = True )])
async def _vorschlag(ctx: SlashContext, nachricht):
    modules.bottiHelper._logSlashCommand(ctx, botData)   
    if botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel is None:
        await botti.get_user(ids.userIDs.ITZFLUBBY).create_dm()
    sentMessage = await botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel.send("**{0}#{1}** ({2}) hat per SlashCommand folgendes vorgeschlagen: _'{3}'_. | {4}".format(ctx.author.name, ctx.author.discriminator, ctx.author.id, nachricht, modules.bottiHelper._getTimestamp()))
    await sentMessage.add_reaction("✅")
    await sentMessage.add_reaction("💤")
    await sentMessage.add_reaction("❌")

    await ctx.send(content = ":bookmark_tabs: Deine Nachricht wurde erfolgreich zugestellt!", hidden = True) 
    
@botti.event
async def on_slash_command_error(ctx, ex):
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    fullError = ""
    for i in traceback.format_exception(type(ex), ex, ex.__traceback__):
        fullError = fullError + i.replace(os.getcwd()[:-10], "..")
        
    botData.lastError = ":warning: Traceback _(Timestamp: {})_  • Verursacht durch {} [via Slash-Command]\n```py\n{}```".format(modules.bottiHelper._getTimestamp(), msg.author.mention, fullError)
    await modules.bottiHelper._errorMessage(botti, msg, botData, ex)