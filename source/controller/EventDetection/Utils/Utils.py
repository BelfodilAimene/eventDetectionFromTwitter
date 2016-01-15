import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from TFIDFUtilities import *

#--------------------------------------------------------------------------------------------
#         Plot time distribution 
#--------------------------------------------------------------------------------------------

def plotTweetsApparitionInTime(tweets, granularity=3600, dyadic=True) :
    """
    Plot the tweets number signal in time
    """
    firstTweet=min(tweets, key=lambda tweet : tweet.time)
    agg={}
    for tweet in tweets :
        index=int(tweet.delay(firstTweet)/granularity)
        if (index in agg) : agg[index]+=1
        else : agg[index]=1

    xList,yList=[],[]
    for x,y in agg.iteritems() :
        xList.append(firstTweet.time+timedelta(0,x*granularity))
        yList.append(y)
        if (dyadic and granularity>1) :
            if ((x-1) not in agg) :
                xList.append(firstTweet.time+timedelta(0,x*granularity-1))
                yList.append(0)
            if ((x+1) not in agg) :
                xList.append(firstTweet.time+timedelta(0,(x+1)*granularity))
                yList.append(0)
            xList.append(firstTweet.time+timedelta(0,(x+1)*granularity-1))
            yList.append(y)

    xList,yList=zip(*sorted(zip(xList,yList),key = lambda element : element[0])) 

    plt.figure(1)
    plt.clf()
    plt.plot(xList,yList, '-', markerfacecolor='k',markeredgecolor='k', markersize=1)
    plt.xlabel("Temps")
    plt.ylabel("Nombre de tweets")
    plt.title('Nombre total de tweets {0}'.format(len(tweets)))
    plt.show()

def plotTermApparitionInTime(tweets,term, granularity=3600, dyadic=True) :
    """
    Plot a term occurence signal in time
    """
    firstTweet=min(tweets, key=lambda tweet : tweet.time)
    lastTweet=max(tweets, key=lambda tweet : tweet.time)
    lastIndex=int(lastTweet.delay(firstTweet)/granularity)
    agg={}
    TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=0, remove_noise_with_poisson_Law=False)
    if term not in TweetPerTermMap :
        print "This term dosent exist in no tweets"
        return
    tweetOfTerm=[tweets[k] for k in TweetPerTermMap[term]]
    
    for tweet in tweetOfTerm :
        index=int(tweet.delay(firstTweet)/granularity)
        if (index in agg) : agg[index]+=1
        else : agg[index]=1

    xList,yList=[],[]
    for x,y in agg.iteritems() :
        xList.append(firstTweet.time+timedelta(0,x*granularity))
        yList.append(y)
        if (dyadic and granularity>1) :
            if ((x-1) not in agg) :
                xList.append(firstTweet.time+timedelta(0,x*granularity-1))
                yList.append(0)
            if ((x+1) not in agg) :
                xList.append(firstTweet.time+timedelta(0,(x+1)*granularity))
                yList.append(0)
            xList.append(firstTweet.time+timedelta(0,(x+1)*granularity-1))
            yList.append(y)

    xList,yList=zip(*sorted(zip(xList,yList),key = lambda element : element[0]))
    
    plt.figure(1)
    plt.clf()
    plt.plot(xList,yList, '-', markerfacecolor='k',markeredgecolor='k', markersize=1)
    plt.xlabel("Temps")
    plt.ylabel("Nombre de tweets contenant le terme")
    plt.title('Nombre total de tweets contenant le terme "{1}" = {0}'.format(len(tweetOfTerm),term.encode("utf-8")))
    plt.show()
    
def plotTermApparitionInTimeWithOrder(tweets,topTermOrder=0, granularity=3600, dyadic=True) :
    """
    Plot a term occurence signal in time
    """
    firstTweet=min(tweets, key=lambda tweet : tweet.time)
    lastTweet=max(tweets, key=lambda tweet : tweet.time)
    lastIndex=int(lastTweet.delay(firstTweet)/granularity)
    agg={}
    TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=0, remove_noise_with_poisson_Law=False)

    term = sorted(list(TweetPerTermMap),key=lambda element : len(TweetPerTermMap[element]),reverse=True)[topTermOrder]
    tweetOfTerm=[tweets[k] for k in TweetPerTermMap[term]]
    
    for tweet in tweetOfTerm :
        index=int(tweet.delay(firstTweet)/granularity)
        if (index in agg) : agg[index]+=1
        else : agg[index]=1

    xList,yList=[],[]
    for x,y in agg.iteritems() :
        xList.append(firstTweet.time+timedelta(0,x*granularity))
        yList.append(y)
        if (dyadic and granularity>1) :
            if ((x-1) not in agg) :
                xList.append(firstTweet.time+timedelta(0,x*granularity-1))
                yList.append(0)
            if ((x+1) not in agg) :
                xList.append(firstTweet.time+timedelta(0,(x+1)*granularity))
                yList.append(0)
            xList.append(firstTweet.time+timedelta(0,(x+1)*granularity-1))
            yList.append(y)

    xList,yList=zip(*sorted(zip(xList,yList),key = lambda element : element[0]))
    
    plt.figure(1)
    plt.clf()
    plt.plot(xList,yList, '-', markerfacecolor='k',markeredgecolor='k', markersize=1)
    plt.xlabel("Temps")
    plt.ylabel("Nombre de tweets contenant le terme")
    plt.title('Nombre total de tweets contenant le terme "{1}" = {0}'.format(len(tweetOfTerm),term.encode("utf-8")))
    plt.show()

#--------------------------------------------------------------------------------------------
#         Plot space distribution 
#--------------------------------------------------------------------------------------------

def plotTweetsInSpaceDistribution(tweets) :
    xList,yList=zip(*[(tweet.position.latitude,tweet.position.longitude) for tweet in tweets])
    plt.figure(1)
    plt.clf()
    plt.plot(xList,yList, 'o', markerfacecolor='k',markeredgecolor='k', markersize=2)
    plt.xlabel("latitude")
    plt.ylabel("longitude")
    plt.title('Nombre total de tweets {0}'.format(len(tweets)))
    plt.show()

def plotTermInSpaceDistribution(tweets,term) :
    TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=0, remove_noise_with_poisson_Law=False)
    if term not in TweetPerTermMap :
        print "This term dosent exist in no tweets"
        return
    tweetOfTerm=[tweets[k] for k in TweetPerTermMap[term]]
    xListBack,yListBack=zip(*[(tweet.position.latitude,tweet.position.longitude) for tweet in tweets])
    xList,yList=zip(*[(tweet.position.latitude,tweet.position.longitude) for tweet in tweetOfTerm])

    plt.figure(1)
    plt.clf()
    plt.plot(xListBack,yListBack, 'o', markerfacecolor='0.75',markeredgecolor='0.75', markersize=2)
    plt.plot(xList,yList, 'o', markerfacecolor='r',markeredgecolor='r', markersize=2)
    plt.xlabel("latitude")
    plt.ylabel("longitude")
    plt.title('Nombre total de tweets contenant le terme "{1}" = {0}'.format(len(tweetOfTerm),term.encode("utf-8")))
    plt.show()
    
def plotTermInSpaceDistributionWithOrder(tweets,topTermOrder=0) :
    TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=0, remove_noise_with_poisson_Law=False)
    term = sorted(list(TweetPerTermMap),key=lambda element : len(TweetPerTermMap[element]),reverse=True)[topTermOrder]
    tweetOfTerm=[tweets[k] for k in TweetPerTermMap[term]]
    xListBack,yListBack=zip(*[(tweet.position.latitude,tweet.position.longitude) for tweet in tweets])
    xList,yList=zip(*[(tweet.position.latitude,tweet.position.longitude) for tweet in tweetOfTerm])

    plt.figure(1)
    plt.clf()
    plt.plot(xListBack,yListBack, 'o', markerfacecolor='0.75',markeredgecolor='0.75', markersize=2)
    plt.plot(xList,yList, 'o', markerfacecolor='r',markeredgecolor='r', markersize=2)
    plt.xlabel("latitude")
    plt.ylabel("longitude")
    plt.title('Nombre total de tweets contenant le terme "{1}" = {0}'.format(len(tweetOfTerm),term.encode("utf-8")))
    plt.show()
    
#--------------------------------------------------------------------------------------------
#         Plot similarity distribution 
#--------------------------------------------------------------------------------------------
  
def plotSimilarityDistribution(sourcePath, granularity=0.001, maxI=100) :
    """
    Plot the similarity distribution of the source path (written in the same syntax used for ModularityOptimizer jar input)
    wrt. of a granularity and a maximum I (the last tweet order) 
    """
    sourceFile=open(sourcePath, 'r')
    distribution=[0]*(int(1/granularity)+1)
    values=[i*granularity for i in range(len(distribution))]
    lastI=0
    newI=0
    numberOfNeighboor=0
    numberOfElements=0
    for line in sourceFile :
        liste=line.split("\t")
        sim=float(liste[2])
        newI=int(liste[0])
        if (newI>lastI) :
            print lastI,":",numberOfNeighboor
            numberOfElements+=numberOfNeighboor
            numberOfNeighboor=0
        else : numberOfNeighboor+=1
        if (newI==maxI) : break
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
