import datetime
import modules.bottiHelper
import modules.data.ids as ids
import modules.calendar
import modules.info
import modules.lerngruppe
import modules.mensa
import modules.utils
import os
import traceback

from __main__ import botti, slash

from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.utils import manage_commands

from modules.data.botData import botData

@slash.slash(name="wochenplan", description="Zeigt dir deinen personalisierten Wochenplan an.", guild_ids = [ ids.serverIDs.ETIT_KIT ], 
    options = [ manage_commands.create_option(
        name = "date",
        description = "Optionales Datum im Format TT.MM.JJJJ",
        option_type = 3,
        required = False 
    )])
async def _wochenplan(ctx: SlashContext, date = ""):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    date = date if date != "" else datetime.datetime.now().strftime("%d.%m.%Y")
    dummyMessage = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "{prefix}wochenplan {date} slash".format(prefix = botData.botPrefix, date = date))
    embed = await modules.calendar.wochenplan(botti, dummyMessage, botData)
    await ctx.send(content = "Slash-Command: Wochenplan")
    await ctx.send(content = "{userMention} Dies ist dein **persönlicher** Wochenplan, basierend auf deinen Rollen!".format(userMention = ctx.author.mention), embed = embed, hidden = True)

@slash.slash(name="convert", description="Konvertiert einen Inhalt.", guild_ids = [ ids.serverIDs.ETIT_KIT ], 
    options = [ manage_commands.create_option(
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
        } 
    ],
    required = True ),
    manage_commands.create_option(
        name = "inhalt",
        description = "Inhalt zum Konvertieren.",
        option_type = 3,
        required = True 
    )])
async def _convert(ctx, typ, inhalt):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "!convert " + typ + " " + inhalt)
    await ctx.send(content = "Slash-Command: Convert")
    await modules.utils.convert(botti, msg, botData)

@slash.slash(name="klausuren", description="Zeigt dir personalisiert deine anstehenden Klausuren an.", guild_ids = [ ids.serverIDs.ETIT_KIT ])
async def _klausuren(ctx: SlashContext):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    dummyMessage = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "{prefix}klausuren slash".format(prefix = botData.botPrefix))
    examString = await modules.calendar.klausuren(botti, dummyMessage, botData)
    await ctx.send(content = "Slash-Command: Klausuren")   
    await ctx.send(content = "Dies sind deine **persönlichen** Klausuren, basierend auf deinen Rollen! {authorMention}\n{examString}".format(examString = examString, authorMention = ctx.author.mention), hidden = True)    

@slash.subcommand(base="lerngruppe", name="add", description="Fügt einen Nutzer einer Lerngruppe hinzu.", guild_ids = [ ids.serverIDs.ETIT_KIT ], 
    options = [ 
        manage_commands.create_option(
            name = "user",
            description = "Nutzer der hinzugefügt werden soll.",
            option_type = 6,
            required = True
        )
    ])
async def _lerngruppe(ctx, user):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    commandArgs = "{prefix}lerngruppe add {userMention}".format(prefix = botData.botPrefix, userMention = user.mention)
    
    print(commandArgs)
    
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, commandArgs, [ { "id": user.id } ])
    await ctx.send(content = "Slash-Command: Lerngruppe")
    await modules.lerngruppe.lerngruppe(botti, msg, botData)

@slash.slash(name="userinfo", description="Zeigt Informationen über einen Benutzer an!", guild_ids = [ ids.serverIDs.ETIT_KIT ], 
    options = [ manage_commands.create_option(
        name = "benutzer",
        description = "Hier musst du einen Benutzer auswählen.",
        option_type = 6,
        required = True 
    )])
async def _userinfo(ctx, benutzer):
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    msg.mentions = [ benutzer ]
    await ctx.send(content = "Slash-Command: Userinfo")
    await modules.info.userinfo(botti, msg, botData)

@slash.slash(name="vorschlag", description="Sag mir deine Meinung! Gebe Verbesserungsvorschläge, oder -ideen ab!", guild_ids = [ ids.serverIDs.ETIT_KIT ], 
    options = [ manage_commands.create_option(
        name = "nachricht",
        description = "Hier kannst du deine Meinung reinschreiben. Bitte sei nicht zu böse :) !",
        option_type = 3,
        required = True 
    )])
async def _vorschlag(ctx: SlashContext, nachricht):
    modules.bottiHelper._logCommand(botData, ctx = ctx)   
    if botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel is None:
        await botti.get_user(ids.userIDs.ITZFLUBBY).create_dm()
    sentMessage = await botti.get_user(ids.userIDs.ITZFLUBBY).dm_channel.send("**{0}#{1}** ({2}) hat per SlashCommand folgendes vorgeschlagen: _'{3}'_. | {4}".format(ctx.author.name, ctx.author.discriminator, ctx.author.id, nachricht, modules.bottiHelper._getTimestamp()))
    await sentMessage.add_reaction("✅")
    await sentMessage.add_reaction("💤")
    await sentMessage.add_reaction("❌")
    await sentMessage.add_reaction("👑")

    await ctx.send(content = ":bookmark_tabs: Deine Nachricht wurde erfolgreich zugestellt!", hidden = True) 

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
    modules.bottiHelper._logCommand(botData, ctx = ctx)
    commandArgs = "!mensa " + mensa + " "
    if wochentag != "none":
        commandArgs = commandArgs + wochentag

    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, commandArgs)
    await ctx.send(content = "Slash-Command: Mensa")
    await modules.mensa.mensa(botti, msg, botData)

@botti.event
async def on_slash_command_error(ctx, ex):
    msg = modules.bottiHelper._createDummyMessage(ctx.author, ctx.channel, "")
    fullError = ""
    for i in traceback.format_exception(type(ex), ex, ex.__traceback__):
        fullError = fullError + i.replace(os.getcwd()[:-10], "..")
        
    botData.lastError = ":warning: Traceback _(Timestamp: {})_  • Verursacht durch {} [via Slash-Command]\n```py\n{}```".format(modules.bottiHelper._getTimestamp(), msg.author.mention, fullError)
    await modules.bottiHelper._errorMessage(botti, msg, botData, ex)
