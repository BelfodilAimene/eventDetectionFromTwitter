import os
from pymongo import MongoClient

from ...model.Tweet import Tweet
from ...model.Position import Position
from TransformationUtilities import getTweetFromJSONFile,getTweetFromCSVLine

class MongoDBHandler :
    def __init__(self,port=27017,database_name='Twitter',collection_name="tweets") :
        self.client = MongoClient('localhost', port)
        self.db = self.client[database_name]
        self.collection=self.db[collection_name]

    def saveTweet(self,tweet) :
        self.collection.insert_one(MongoDBHandler.getDocumentFromTweet(tweet))
        
    def saveTweets(self,tweets) :
        self.collection.insert([MongoDBHandler.getDocumentFromTweet(tweet) for tweet in tweets])

    def getAllTweets(self,limit=50) :
        documents=self.collection.find()[0:limit]
        tweets=[MongoDBHandler.getTweetFromDocument(document) for document in documents]
        return tweets

    def saveTweetsFromJSONRepository(self,jsonDirectoryPath,ensureHavePosition=True) :
        jsonFilePaths=os.listdir(jsonDirectoryPath)
        i=1
        for jsonFilePath in jsonFilePaths :
            if (i%100==0) : print i
            i+=1
            path=os.path.join(jsonDirectoryPath,jsonFilePath)
            try :
                tweet=getTweetFromJSONFile(path)
                if (not ensureHavePosition or tweet.position) : self.saveTweet(tweet)
            except ValueError :
                print jsonFilePath

    def saveTweetsFromCSVFile(self,csvFilePath,ensureHavePosition=True,keepOnlyTweetsWithHashtags=True) :
        i=0
        SHOW_RATE=1000
        with open(csvFilePath) as f :
            line=f.readline() #Header
            print "Filling data base"
            for line in f :
                tweet=getTweetFromCSVLine(line)
                if ((not ensureHavePosition or tweet.position) and (not keepOnlyTweetsWithHashtags or tweet.hashtags)) :
                    self.saveTweet(tweet)
                    i+=1
                    if (i%SHOW_RATE==0) : print "\t",i
        
    @staticmethod
    def getDocumentFromTweet(tweet) :
        dictionary={}
        dictionary["_id"]=tweet.id
        dictionary["userId"]=tweet.userId
        dictionary["text"]=tweet.text
        dictionary["hashtags"]=tweet.hashtags
        dictionary["time"]=tweet.time
        dictionary["position"]=None
        if (tweet.position) :
            dictionary["position"]=[tweet.position.latitude,tweet.position.longitude]
        return dictionary

    @staticmethod
    def getTweetFromDocument(document) :
        _id=document["_id"]
        userId=document["userId"]
        text=document["text"]
        hashtags=document["hashtags"]
        time=document["time"]
        position=None
        if (document["position"]) :
            position=Position(document["position"][0],document["position"][1])
        return Tweet(_id,userId,text,hashtags,time,position)
