from ..model.Tweet import Tweet
from ..model.Position import Position
from pymongo import MongoClient
import json

class MongoDBHandler :
    def __init__(self,port=27017,database_name='Twitter') :
        self.client = MongoClient('localhost', port)
        self.db = self.client[database_name]

    def saveTweets(self,tweets) :
        collection = self.db['tweets']
        collection.insert([MongoDBHandler.getDocumentFromTweet(tweet) for tweet in tweets])

    def getAllTweets(self) :
        collection = self.db['tweets']
        tweets=[MongoDBHandler.getTweetFromDocument(document) for document in collection.find()]
        return tweets

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
        
        
        
        
        
        
   
        
