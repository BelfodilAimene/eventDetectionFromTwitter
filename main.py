from source.controller.MyTwitterAPI import MyTwitterAPI
from source.controller.EventDetection.LEDSimilarityMatrixBuilder import LEDSimilarityMatrixBuilder
from source.controller.EventDetection.MEDSimilarityMatrixBuilder import MEDSimilarityMatrixBuilder
from source.controller.MongoDBHandler import MongoDBHandler
from source.controller.EventDetection.EventDetector import EventDetector

from source.model.Event import Event 

import time

def main() :
    
    staringTime=time.time()

    
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets()[0:50]
    """
    api = MyTwitterAPI("twitter_config_file.txt")
    tweets = api.getTweets(count=1,export=True)
    mongoDBHandler.saveTweets(tweets)
    """
    
    #s=LEDSimilarityMatrixBuilder(timeThreshold=1800,distanceThreshold=100)
    s=MEDSimilarityMatrixBuilder(timeResolution=60,distanceResolution=100,scaleNumber=4)
    
    eventDetector=EventDetector(tweets,s)
    events=eventDetector.getEvents()
    print "\n\n\n"
    print "-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40
    for event in events :
        event.printMySelf()
    eventDetector.drawEvents()

    print "-"*40
    elapsed_time=(time.time()-staringTime)
    print "Elapsed time : {0}s, {1} event detected".format(elapsed_time,len(events))
    

    
main()
