from source.controller.DataManagement.MyTwitterAPI import MyTwitterAPI
from source.controller.DataManagement.MongoDBHandler import MongoDBHandler

from source.controller.EventDetection.SimilarityMatrixBuilder.LEDSimilarityMatrixBuilder import LEDSimilarityMatrixBuilder
from source.controller.EventDetection.SimilarityMatrixBuilder.MEDSimilarityMatrixBuilder import MEDSimilarityMatrixBuilder
from source.controller.EventDetection.EventDetector import EventDetector
from source.model.Event import Event 
import time

LED_SIM=0
MED_SIM=1

def getTweetsFromTwitterAndSave(count=100,export=False) :
    mongoDBHandler=MongoDBHandler()
    api = MyTwitterAPI("twitter_config_file.txt")
    tweets = api.getTweets(count=count,export=export)
    mongoDBHandler.saveTweets(tweets)

def getTweetsFromJSONRepositoryAndSave(repositoryPath="E:\\tweets") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)

def detectEvents(limit=200,similarityType=MED_SIM,printEvents=False,drawEvents=False) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)

    if similarityType==LED_SIM :
        s=LEDSimilarityMatrixBuilder(timeThreshold=1800,distanceThreshold=100)
    else :
        s=MEDSimilarityMatrixBuilder(timeResolution=1800,distanceResolution=100,scaleNumber=4)

    eventDetector=EventDetector(tweets,s)
    events=eventDetector.getEvents()
    
    print "\n"+"-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40

    if printEvents :
        for e in events :
            print e
            print "_"*40

    if drawEvents :
        print "drawing ..."
        eventDetector.drawEvents()

    return events
    

def main() :
    staringTime=time.time()

    events=detectEvents(limit=50000,similarityType=LED_SIM)

    elapsed_time=(time.time()-staringTime)
    print "-"*40
    print "Elapsed time : {0}s, {1} event detected".format(elapsed_time,len(events))
    print "-"*40
    
    

    
main()
