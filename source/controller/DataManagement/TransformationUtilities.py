import json,re,datetime
from ...model.Tweet import Tweet
from ...model.Position import Position
from dateutil import parser

#-------------------------------------------------------------
#            Text processing utilities
#-------------------------------------------------------------

UTF_CHARS = r'a-z0-9_\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff'
HASHTAG_EXP = r'(^|[^0-9A-Z&/]+)(#|\uff03)([0-9A-Z_]*[A-Z_]+[%s]*)' % UTF_CHARS
HASHTAG_REGEX = re.compile(HASHTAG_EXP, re.IGNORECASE)

def getHashtags(text) :
    tags=HASHTAG_REGEX.findall(text)
    tags=[element[2] for element in tags]
    return tags

#-------------------------------------------------------------
#            JSON Sources
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
    time=parser.parse(s)
    #-----Position ----------------------------------
    position=None
    if jsonData["coordinates"] :
        latitude=jsonData["coordinates"]["coordinates"][1]
        longitude=jsonData["coordinates"]["coordinates"][0]
        position=Position(latitude,longitude)
    return Tweet(_id,userId,text,hashtags,time,position)

def getTweetFromJSONFile(jsonFilePath) :
    with open(jsonFilePath) as f :
        return getTweetFromJSON(f.readline())

#-------------------------------------------------------------
#            CSV Sources (as Mehdi File template)
#-------------------------------------------------------------

def getTweetFromCSVLine(csvLine) :
    NULL_STRING='null'

    line = csvLine.strip().split(",")

    _id=line[0]
    userId=line[12]
    text=line[10]
    if (text==NULL_STRING) : text=""
    
    time=datetime.datetime(int(line[5]),int(line[4]),int(line[3]),int(line[2]),int(line[1]))
    
    position=None
    if line[6]!=NULL_STRING :
        longitude=float(line[6])
        latitude=float(line[7])
        position=Position(latitude,longitude)

    hashtags=getHashtags(text)
    
    return Tweet(_id,userId,text,hashtags,time,position)
#-------------------------------------------------------------
