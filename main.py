import time
from source.controller.DataManagement.MyTwitterAPI import MyTwitterAPI
from source.controller.DataManagement.MongoDBHandler import MongoDBHandler

from source.controller.EventDetection.SimilarityMatrixBuilder.LEDSimilarityMatrixBuilder import LEDSimilarityMatrixBuilder
from source.controller.EventDetection.SimilarityMatrixBuilder.MEDSimilarityMatrixBuilder import MEDSimilarityMatrixBuilder
from source.controller.EventDetection.OptimisedEventDetectorMEDBased import OptimisedEventDetectorMEDBased
from source.controller.EventDetection.EventDetector import EventDetector


LED_SIM=0
MED_SIM=1
NUMBER_OF_TWEETS=56021

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

    if printEvents : eventDetector.showTopEvents(top=10)

    if drawEvents :
        print "drawing ..."
        eventDetector.drawEvents()
    
    return events

def detectEventsMED(limit=200,minimalTermPerTweet=5,remove_noise_with_poisson_Law=False) :
    mongoDBHandler=MongoDBHandler()
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    eventDetector=OptimisedEventDetectorMEDBased(tweets,timeResolution=1800,distanceResolution=100,scaleNumber=4)
    events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
    print "\n"+"-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40
    eventDetector.showTopEvents(top=10)
    return events
    

def main() :
    staringTime=time.time()

    #detectEvents(limit=300,similarityType=MED_SIM,printEvents=True)
    detectEventsMED(limit=300,minimalTermPerTweet=5,remove_noise_with_poisson_Law=False)
    
    elapsed_time=(time.time()-staringTime)

    print "-"*40
    print "Elapsed time : {0}s".format(elapsed_time)
    print "-"*40
    

import numpy as np
import matplotlib.pyplot as plt    
def studySimilarityFile(sourcePath="D:\PRJS\input.txt", granularity=0.001) :
    sourceFile=open(sourcePath, 'r')
    distribution=[0]*(int(1/granularity)+1)
    values=[i*granularity for i in range(len(distribution))]
    lastI=0
    newI=0
    numberOfNeighboor=0
    numberOfElements=0
    MAXI=100
    for line in sourceFile :
        liste=line.split("\t")
        sim=float(liste[2])
        newI=int(liste[0])
        if (newI>lastI) :
            print lastI,":",numberOfNeighboor
            numberOfElements+=numberOfNeighboor
            numberOfNeighboor=0
        else : numberOfNeighboor+=1
        if (newI==MAXI) : break
        distribution[int(sim/granularity)]+=1
        lastI=newI 
    sourceFile.close()
    plt.figure(1)
    plt.clf()
    plt.plot(values,distribution, '-', markerfacecolor='k',markeredgecolor='k', markersize=1)
    plt.xlabel("values")
    plt.ylabel("number")
    plt.title('Number of elements {0}'.format(numberOfElements))
    plt.show()

def cleanFile(sourcePath="D:\PRJS\input3.txt",destinationPath="D:\PRJS\input4.txt", MINSIM=0.01) :
    sourceFile=open(sourcePath, 'r')
    destinationFile=open(destinationPath, 'w')
    lastI=0
    newI=0
    for line in sourceFile :
        liste=line.split("\t")
        sim=float(liste[2])
        newI=int(liste[0])
        if (newI>lastI and newI%20==0) : print newI
        lastI=newI
        if (sim<MINSIM) : continue
        destinationFile.write(line)
    sourceFile.close()
    destinationFile.close()

    
    
    
main()
#cleanFile(MINSIM=0.5)
#studySimilarityFile()
