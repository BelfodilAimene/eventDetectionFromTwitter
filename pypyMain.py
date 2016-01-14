import time
from source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from source.controller.EventDetection.OptimisedEventDetectorMEDBased import OptimisedEventDetectorMEDBased
#---------------------------------------------------------------------------------------------------------------------------------------------
MIN_TERM_OCCURENCE=5
REMOVE_NOISE_WITH_POISSON_LAW=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0.5

NUMBER_OF_TWEETS=56021
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromTwitterAndSave(count=100,export=False) :
    mongoDBHandler=MongoDBHandler()
    api = MyTwitterAPI("twitter_config_file.txt")
    tweets = api.getTweets(count=count,export=export)
    mongoDBHandler.saveTweets(tweets)
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromJSONRepositoryAndSave(repositoryPath="E:\\tweets") :
    mongoDBHandler=MongoDBHandler()
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)
#---------------------------------------------------------------------------------------------------------------------------------------------
def detectEvents(limit=300,minimalTermPerTweet=MIN_TERM_OCCURENCE,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)

    eventDetector=OptimisedEventDetectorMEDBased(tweets,timeResolution=TIME_RESOLUTION,distanceResolution=DISTANCE_RESOLUTION,scaleNumber=SCALE_NUMBER,minSimilarity=MIN_SIMILARITY)
    events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
        
    print ""
    print "-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40
    
    if printEvents : eventDetector.showTopEvents(top=10)

    return events
#---------------------------------------------------------------------------------------------------------------------------------------------
def main(limit=300) :
    staringTime=time.time()
    detectEvents(limit=limit)
    elapsed_time=(time.time()-staringTime)
    print "-"*40
    print "Elapsed time : {0}s".format(elapsed_time)
    print "-"*40
#---------------------------------------------------------------------------------------------------------------------------------------------
main(limit=NUMBER_OF_TWEETS)
