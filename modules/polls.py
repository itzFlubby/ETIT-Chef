import discord
import modules.bottiHelper

def _getStringAfter(string, after):
    return string[(string.find(after)+len(after)):]

async def _updatePoll(message, vote, user, botData):
    embed = message.embeds[0]
    for run, field in enumerate(embed.fields):
        if field.name == vote:
            if user.mention in field.value: # If user already voted
                mentionBegin = field.value.find(user.mention)
                mentionEnd = mentionBegin + len(user.mention)
                clicked = field.value[mentionEnd:].split("`")[0]
                restValue = _getStringAfter(field.value[mentionEnd:], "`\n`")
                
                if not clicked:
                    clicked = 2
                else:
                    clicked = int(clicked[3:]) + 1
                
                newValue = field.value[:mentionEnd] + " x " + str(clicked) + "`\n`" + restValue
                embed.set_field_at(index = run, name = field.name, value = newValue)
                break
            embed.set_field_at(index = run, name = field.name, value = (user.mention + "`\n`") if (field.value == "Keine Stimmen") else field.value + user.mention + "`\n`")
            break
    await message.edit(embed = embed)
    
async def createpoll(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl erstellt eine Umfrage.
    !createpoll {TITLE} {OPTIONS}
    {TITLE} "String"
    {OPTIONS} OPT1,OPT2,OPT3,...
    !createpoll "Ist dieses Feature der Hammer?!" ja, nein, weiß ich nicht
    """
    if len(message.content.split(" ")) < 2 or len(message.content.split("\"")) < 2 or len(message.content.split(",")) < 2:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "createpoll"))      
        return 
    
    embed = discord.Embed(
        title = "Abstimmung",
        color = 0xff5500,
        description = "{pollTopic}".format(pollTopic = message.content.split("\"")[1])
    )
    
    options = message.content.split("\"")[2][1:].split(",")
    for option in options:
        option = option[1:] if option[0] == " " else option # Remove whitespace if user set one
        embed.add_field(name = option, value = "Keine Stimmen")
    
    embed.add_field(name = "Abstimmung von", value = message.author.mention, inline = False)
    embed.set_thumbnail(url = message.author.avatar.url)
    embed.set_footer(text = "Stand: {timestamp}".format(timestamp = modules.bottiHelper._getTimestamp()))
    
    view = discord.ui.View(timeout = None)
    for run, field in enumerate(embed.fields):
        if run == len(embed.fields) - 1:
            break # If last element reached, don't make "Abstimmung von" a button
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.secondary, label = field.name, custom_id = field.name))
        
    message = await modules.bottiHelper._sendMessage(message, embed = embed, view = view)
    await _updatePoll(message, None, None, botData)
    
async def repostpoll(botti, message, botData):
    """
    Reserviert für Moderator oder höher
    Dieser Befehl postet eine Umfrage erneut.
    !repostpoll {ID}
    {ID} Message-ID
    !repostpoll 1234567891011121314
    """
    if len(message.content.split(" ")) < 2:
        await modules.bottiHelper._sendMessagePingAuthor(message, modules.bottiHelper._invalidParams(botData, "repostpoll"))      
        return 
        
    message = await message.channel.fetch_message(int(message.content.split(" ")[1]))
    if message == None:
        await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Diese Abstimmung konnte ich nicht finden!")
        return
        
    if len(message.embeds) != 0:
        if message.embeds[0].title != "Abstimmung":
            await modules.bottiHelper._sendMessagePingAuthor(message, ":x: Bei dieser Nachricht handelt es sich um keine Abstimmung!")
            return  
            
    view = discord.ui.View(timeout = None)
    for run, field in enumerate(message.embeds[0].fields):
        if run == len(message.embeds[0].fields) - 1:
            break # If last element reached, don't make "Abstimmung von" a button
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.secondary, label = field.name, custom_id = field.name))
     
    await message.delete()
    await modules.bottiHelper._sendMessage(message, content = ":arrow_double_down: Die Umfrage wurde nach unten gezogen!", embed = message.embeds[0], view = view)