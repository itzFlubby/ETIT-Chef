import discord
import modules.bottiHelper
import modules.data.ids as ids

from __main__ import botti

def _constructAsset(id):
    return "https://cdn.discordapp.com/app-assets/" + str(ids.userIDs.ETIT_CHEF) + "/" + str(id)

def _constructDefaultEmbed(title, description, color = 0x0, thumbnail = None, footer = None, author = None, url = discord.Embed.Empty):
    embed = discord.Embed(
        title = title,
        description = description,
        color = color,
        url = url
    )
    
    embed.set_thumbnail(url = thumbnail if thumbnail != None else botti.user.avatar.url)
    embed.set_author(name = _ifKeySet(author, "name", "{user.name}#{user.discriminator}".format(user = botti.user)), icon_url = _ifKeySet(author, "icon_url", botti.user.avatar.url))
    embed.set_footer(text = _ifKeySet(footer, "text", "Stand: " + modules.bottiHelper._getTimestamp()), icon_url = _ifKeySet(footer, "icon_url", "https://cdn.discordapp.com/app-assets/" + str(ids.userIDs.ETIT_CHEF) + "/" + str(ids.assetIDs.PYTHON_LOGO)))
    
    return embed

def _constructDummyMessage(author, channel, content = "", mentions = []):
    dataDict = { 
        "id": 0, 
        "webhook_id": 0, 
        "attachments": [], 
        "embeds": {}, 
        "application": 0, 
        "activity": 0, 
        "edited_timestamp": 0, 
        "type": 0, 
        "pinned": 0, 
        "mention_everyone": 0, 
        "tts": 0, 
        "content": content, 
        "nonce": 0,
        "mentions": mentions
    }
    msg = discord.Message(state = 0, channel = channel, data = dataDict)
    msg.author = author
    return msg  

def _constructEmojiString(emoji):
    return "<{emojiNoBracket}>".format(emojiNoBracket = _constructEmojiStringNoBracket(emoji))

def _constructEmojiStringNoBracket(emoji):
    return "{isAnimated}:{emojiName}:{emojiID}".format(isAnimated = ("a" if emoji["animated"] else ""), emojiName = emoji["name"], emojiID = emoji["id"])
 
def _ifKeySet(dict, key, default = None):
    if dict != None and dict.get(key):
        return dict[key]
    return default