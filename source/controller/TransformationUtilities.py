import ntpath
import os
import tweepy

import json
from dateutil.parser import parse
import warnings
warnings.filterwarnings("ignore", category=UnicodeWarning)

from ..model.Tweet import Tweet
from ..model.Position import Position


#-------------------------------------------------------------
def getTweetFromJSON(jsonText) :
    jsonData = json.loads(jsonText)
    _id=jsonData["id"]
    userId=jsonData['user']['id']
    text=jsonData["text"]
    #---- Hashtags ----------------------------------
    hashtags=[element["text"] for element in jsonData["entities"]["hashtags"]]
    #------------------------------------------------
    s=jsonData["created_at"]
    time=parse(s)
    #-----Position ----------------------------------
    position=None
    if jsonData["coordinates"] :
        latitude=jsonData["coordinates"]["coordinates"][1]
        longitude=jsonData["coordinates"]["coordinates"][0]
        position=Position(latitude,longitude)
    return Tweet(_id,userId,text,hashtags,time,position)

#-------------------------------------------------------------
def getTweetFromJSONFile(jsonFilePath) :
    with open(jsonFilePath) as f :
        return getTweetFromJSON(f.readline())
#-------------------------------------------------------------


