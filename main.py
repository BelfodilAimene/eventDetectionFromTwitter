import time
from source.model.Event import Event 
from source.controller.DataManagement.MyTwitterAPI import MyTwitterAPI
from source.controller.DataManagement.MongoDBHandler import MongoDBHandler

from source.controller.EventDetection.SimilarityMatrixBuilder.MEDSimilarityMatrixBuilder import MEDSimilarityMatrixBuilder
from source.controller.EventDetection.SimilarityMatrixBuilder.LEDSimilarityMatrixBuilder import LEDSimilarityMatrixBuilder
from source.controller.EventDetection.EventDetector import EventDetector
from source.controller.EventDetection.EventDetectorMEDBased import EventDetectorMEDBased

LED_SIM=0
MED_SIM=1

def getTweetsFromTwitterAndSave(count=100,export=False) :
    mongoDBHandler=MongoDBHandler()
    api = MyTwitterAPI("twitter_config_file.txt")
    tweets = api.getTweets(count=count,export=export)
    mongoDBHandler.saveTweets(tweets)

def getTweetsFromJSONRepositoryAndSave(repositoryPath="E:\\tweets") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFomJSONRepository(repositoryPath)

def detectEvents(limit=200,similarityType=MED_SIM,printEvents=False,drawEvents=False) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)

    if similarityType==LED_SIM : s=LEDSimilarityMatrixBuilder(timeThreshold=1800,distanceThreshold=100)
    else : s=MEDSimilarityMatrixBuilder(timeResolution=1800,distanceResolution=100,scaleNumber=4)

    eventDetector=EventDetector(tweets,s)
    events=eventDetector.getEvents()
    
    print "\n"+"-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40

    if printEvents : eventDetector.showTopKEvents(topk=10)

    if drawEvents :
        print "drawing ..."
        eventDetector.drawEvents()
    
    return events

def detectEvents2(limit=200,minimalTermPerTweet=5,remove_noise_with_poisson_Law=False) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    eventDetector=EventDetectorMEDBased(tweets,timeResolution=1800,distanceResolution=100,scaleNumber=4,userNumberThreshold=3,tweetsNumberThreshold=3)
    events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
    print "\n"+"-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40
    eventDetector.showTopKEvents(topk=10)
    return events
    
NUMBER_OF_TWEETS=56021
def main() :
    staringTime=time.time()

    detectEvents(limit=300,similarityType=MED_SIM,printEvents=True)
    #detectEvents2(limit=300,minimalTermPerTweet=5,remove_noise_with_poisson_Law=False)
    
    elapsed_time=(time.time()-staringTime)

    print "-"*40
    print "Elapsed time : {0}s".format(elapsed_time)
    print "-"*40
    
    

    
main()
