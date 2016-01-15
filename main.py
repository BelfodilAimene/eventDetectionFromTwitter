import time
from source.controller.DataManagement.MyTwitterAPI import MyTwitterAPI
from source.controller.DataManagement.MongoDBHandler import MongoDBHandler

from source.controller.EventDetection.SimilarityMatrixBuilder.LEDSimilarityMatrixBuilder import LEDSimilarityMatrixBuilder
from source.controller.EventDetection.SimilarityMatrixBuilder.MEDSimilarityMatrixBuilder import MEDSimilarityMatrixBuilder
from source.controller.EventDetection.OptimisedEventDetectorMEDBased import OptimisedEventDetectorMEDBased
from source.controller.EventDetection.EventDetector import EventDetector

from source.controller.EventDetection.Utils.Utils import *
#---------------------------------------------------------------------------------------------------------------------------------------------

LED_SIM=0
MED_SIM=1
MED_SIM_WITHOUT_REAL_MATRIX=2

MIN_TERM_OCCURENCE=5
REMOVE_NOISE_WITH_POISSON_LAW=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0

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
def detectEvents(limit=300,similarityType=MED_SIM,minimalTermPerTweet=MIN_TERM_OCCURENCE,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)

    if similarityType==LED_SIM :
        s=LEDSimilarityMatrixBuilder(timeThreshold=TIME_RESOLUTION,distanceThreshold=DISTANCE_RESOLUTION)
        eventDetector=EventDetector(tweets,s)
        events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
    elif similarityType==MED_SIM :
        s=MEDSimilarityMatrixBuilder(timeResolution=TIME_RESOLUTION,distanceResolution=DISTANCE_RESOLUTION,scaleNumber=SCALE_NUMBER,minSimilarity=MIN_SIMILARITY)
        eventDetector=EventDetector(tweets,s)
        events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
    else :
        eventDetector=OptimisedEventDetectorMEDBased(tweets,timeResolution=TIME_RESOLUTION,distanceResolution=DISTANCE_RESOLUTION,scaleNumber=SCALE_NUMBER,minSimilarity=MIN_SIMILARITY)
        events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
        
    print ""
    print "-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40

    if printEvents :
        eventDetector.showTopEvents(top=10)

    return events
#---------------------------------------------------------------------------------------------------------------------------------------------
def showTweetsNumberSignal(limit=300,granularity=3600, dyadic=True) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTweetsApparitionInTime(tweets, granularity=granularity, dyadic=dyadic)

def showTermOccurenceSignalByOrder(limit=300,topTermOrder=0, granularity=3600, dyadic=True) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermApparitionInTimeWithOrder(tweets,topTermOrder=topTermOrder, granularity=granularity, dyadic=dyadic)

def showTermOccurenceSignalByTerm(limit=300,term="#shopping", granularity=3600, dyadic=True) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermApparitionInTime(tweets,term, granularity=granularity, dyadic=dyadic)

def showTweetsSpaceDistribution(limit=300) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTweetsInSpaceDistribution(tweets)

def showTermSpaceDistributionByOrder(limit=300,topTermOrder=0) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermInSpaceDistributionWithOrder(tweets,topTermOrder=topTermOrder)

def showTermSpaceDistributionByTerm(limit=300,term="#shopping") :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermInSpaceDistribution(tweets,term)
#---------------------------------------------------------------------------------------------------------------------------------------------  
def main(limit=300, similarityType=MED_SIM_WITHOUT_REAL_MATRIX) :
    staringTime=time.time()
    detectEvents(limit=limit,similarityType=similarityType)
    elapsed_time=(time.time()-staringTime)
    print "-"*40
    print "Elapsed time : {0}s".format(elapsed_time)
    print "-"*40
#---------------------------------------------------------------------------------------------------------------------------------------------
#main(limit=NUMBER_OF_TWEETS, similarityType=MED_SIM_WITHOUT_REAL_MATRIX)
#showTweetsNumberSignal(limit=NUMBER_OF_TWEETS,granularity=3600, dyadic=True)
#showTermOccurenceSignalByOrder(limit=NUMBER_OF_TWEETS,topTermOrder=300, granularity=3600, dyadic=True)
#showTermOccurenceSignalByTerm(limit=NUMBER_OF_TWEETS,term="bisous", granularity=3600, dyadic=True)
#showTweetsSpaceDistribution(limit=NUMBER_OF_TWEETS)
#showTermSpaceDistributionByOrder(limit=NUMBER_OF_TWEETS,topTermOrder=0)
showTermSpaceDistributionByTerm(limit=NUMBER_OF_TWEETS,term="bisous")
