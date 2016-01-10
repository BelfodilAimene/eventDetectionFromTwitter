import os,urllib,ntpath,json
import tweepy

from ...model.Tweet import Tweet
from ...model.Position import Position

DEFAULT_PARENT_DIRECTORY="Tweets"

class MyTwitterAPI :
    def __init__(self,config_file_path) :
        with open(config_file_path) as f :
            consumer_key=f.readline().strip().split(":")[1].strip()
            consumer_secret=f.readline().strip().split(":")[1].strip()
            access_token=f.readline().strip().split(":")[1].strip()
            access_token_secret=f.readline().strip().split(":")[1].strip()
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(auth)

    def getStatusList(self,latitude=48.85341,longitude=2.3488,radius=8,count=100) :
        geocode="{0},{1},{2}km".format(latitude,longitude,radius)
        statusList=self.api.search(q="exclude:retweets",geocode=geocode,count=count)
        return statusList

    def getTweets(self,latitude=48.85341,longitude=2.3488,radius=8,count=100,export=False,parentDirectory=DEFAULT_PARENT_DIRECTORY) :
        statusList=self.getStatusList(latitude=latitude,longitude=longitude,radius=radius,count=count)
        results=map(MyTwitterAPI.getTweetFromStatus,statusList)
        #------------- Exporting tweets ------------------------------------
        if (export) : map(MyTwitterAPI.exportStatusToJSON,statusList)
        #--------------------------------------------------------------------
        return results

    @staticmethod
    def getTweetFromStatus(status) :
        _id=status.id
        userId=str(status.user.id)
        text=status.text
        #---- Hashtags ----------------------------------
        hashtags=[element["text"] for element in status.entities["hashtags"]]
        #------------------------------------------------
        time=status.created_at
        #-----Position ----------------------------------
        position=None
        if status.coordinates :
            latitude=status.coordinates['coordinates'][1]
            longitude=status.coordinates['coordinates'][0]
            position=Position(latitude,longitude)
        #------------------------------------------------
        return Tweet(_id,userId,text,hashtags,time,position)

    @staticmethod
    def exportStatusToJSON(status,parentDirectory=DEFAULT_PARENT_DIRECTORY) :
        newDirectory=parentDirectory+"/"+str(status.id)+"/"
        if not os.path.exists(newDirectory):
            os.makedirs(newDirectory)

        f = open(newDirectory+str(status.id), 'w')
        json.dump(status._json,f)
        f.close()

        mediapath=""
        if "media" in status.entities :
            for entity in status.entities["media"] :
                if ("media_url_https" in entity) : mediapath=entity["media_url_https"]
                elif ("media_url" in entity) : mediapath=entity["media_url"]
                if (mediapath) : downloadImage(mediapath,newDirectory)



def downloadImage(urlImage,parentDirectory) :
    head, tail = ntpath.split(urlImage)
    urllib.urlretrieve(urlImage, parentDirectory+tail)

    
