import asyncio
import datetime
import discord
import modules.bottiHelper
import modules.data.ids as ids
import requests

from __main__ import botti
from modules.data.botData import botData

async def _cyclicVod():
    while(True):
        await asyncio.sleep(3600 * 2) # 2 hours
        accessToken, refreshToken = _getAccessAndRefreshToken()
        authenticationHeader = {'Authorization': 'Bearer ' + accessToken}
        response = requests.get("https://graph.microsoft.com/v1.0/me/drive/root:/{filePath}{fileName}:/content".format(filePath = botData.onedriveInfo["filePath"], fileName = botData.onedriveInfo["fileName"]), headers = authenticationHeader)
        response.encoding = "utf-8"
        fileContent = response.text
        newLog = fileContent.split("\n")
           
        with open(botData.modulesDirectory + "data/vod/" + botData.onedriveInfo["fileName"], 'r') as f:
            oldLog = f.read().split("\n")
            
        with open(botData.modulesDirectory + "data/vod/" + botData.onedriveInfo["fileName"], 'w', encoding="utf-8") as f:
            f.write(fileContent)
           
        lastCycleLineIndexNew = _getLastCycleDate(newLog) if _getLastCycleDate(newLog) != None else 0
        lastCycleLineIndexOld = _getLastCycleDate(oldLog) if _getLastCycleDate(oldLog) != None else 0
        if newLog[lastCycleLineIndexNew] == oldLog[lastCycleLineIndexOld]:
            continue
        
        elementsString = "{emoji} Letzter Zyklus `@{date}`\n".format(emoji = modules.construct._constructEmojiString(ids.emojiIDs.ILIAS), date = newLog[lastCycleLineIndexNew].split(" - ")[1])
        for run, line in enumerate(newLog[(lastCycleLineIndexOld+1):]):
            if ".mp4" in line:
                elementsString += "```fix\n" + line[8:] + "```" # 8 = len("Writing ")
           
        if not ("```fix\n" in elementsString):
            continue
            
        await discord.utils.get(botti.get_all_channels(), id = ids.channelIDs.VOD_PING).send(elementsString)
        
def _getLastCycleDate(log):
    for lineIndex in range(len(log) - 1, 0, -1): # step in reversed order
        if "Cycle" in log[lineIndex]:
            return lineIndex

def _getAccessAndRefreshToken():
    with open(botData.modulesDirectory + "data/vod/token.txt", 'r') as f:
        token = f.read()
    
    postParameters = {
          'grant_type': 'refresh_token', 
          'client_id': botData.onedriveInfo["client_id"],
          'refresh_token': token 
    }
    response = requests.post('https://login.live.com/oauth20_token.srf', data = postParameters)
    refreshToken = response.json()['refresh_token']
    with open(botData.modulesDirectory + "data/vod/token.txt", 'w+') as f:
        f.write(refreshToken)
    return response.json()['access_token'], refreshToken