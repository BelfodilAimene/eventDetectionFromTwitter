import numpy as np
from math import log,sqrt,pi
import re

DELIMITERS=[",",";",":","!","\?","/","\*","=","\+","-","\."," ","\(","\)","\[","\]","\{","\}","'"]

def getListOfTermFromText(text) :
    #Convert to lower case
    text = text.lower()
    #Convert www.* or https?://* to ""
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',text)
    #Convert @username to ""
    text = re.sub('@[^\s]+','',text)
    #Remove additional white spaces
    text = re.sub('[\s]+', ' ', text)
    #trim
    text = text.strip('\'"')
    #split
    regex="|".join(DELIMITERS)
    terms=re.split(regex,text)
    #clean
    terms=[term for term in terms if 2<len(term)<31]
    return terms

def getTermOccurencesVector(text) :
    termOccurences={}
    terms=getListOfTermFromText(text)
    numberOfTerms=len(terms)
    for term in terms :
        try: termOccurences[term] += 1
        except KeyError: termOccurences[term]  = 1
    return termOccurences

def getTFVector(text) :
    TFVector={}
    terms=getListOfTermFromText(text)
    numberOfTerms=len(terms)
    baseFrequency=1./numberOfTerms if (numberOfTerms>0) else 0
    for term in terms :
        try: TFVector[term] += baseFrequency
        except KeyError: TFVector[term] = baseFrequency  
    return TFVector

S_FOR_FILTERING=[200,400,600,800,1000]
THRESHOLD_FOR_FILTERING=500
DEG_LATITUDE_IN_M = 111320 #1 degree in latitude is equal to 111320 m

def getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=5, remove_noise_with_poisson_Law=True) :
    numberOfTweets=len(tweets)
    TFVectors=[]
    IDFVector={}
    TweetPerTermMap={}
    i=0

    minLat=maxLat=tweets[0].position.latitude
    minLon=maxLon=tweets[0].position.longitude

    #TFVecrors construction
    for tweet in tweets :

        #TFVectors construction
        TFVector=getTFVector(tweet.text)
        TFVectors.append(TFVector)
        for term in TFVector :
            try: IDFVector[term] += 1
            except KeyError: IDFVector[term] = 1
            try: TweetPerTermMap[term].add(i)
            except KeyError: TweetPerTermMap[term] = set([i])

        #For estimating the total area for noise filtering
        if (tweet.position.latitude<minLat) : minLat=tweet.position.latitude
        elif (tweet.position.latitude>maxLat) : maxLat=tweet.position.latitude
        if (tweet.position.longitude<minLon) : minLon=tweet.position.longitude
        elif (tweet.position.longitude>maxLon) : maxLon=tweet.position.longitude

        i+=1

    totalArea=(maxLat-minLat)*(maxLon-minLon)*DEG_LATITUDE_IN_M*DEG_LATITUDE_IN_M

    #-----------------------------------------------------------------------
    """
    print "Number of term : ", len(TweetPerTermMap)
    print "Number of non empty tweets : ",len([1 for tfv in TFVectors if len(tfv)>0])
    """
    #-----------------------------------------------------------------------

    #IDFVector preparation and noisy terms filtering
    for term in IDFVector :
        termToDelete=False
        numberOfTweetOfThisTerm=IDFVector[term]
        
        #Eliminate term that appear less than minimalTermPerTweet
        if (numberOfTweetOfThisTerm<minimalTermPerTweet) : termToDelete=True
            
        #Eliminate terms that have poisson distribution in space
        elif (remove_noise_with_poisson_Law) :
            tweetsOfTerm=list(TweetPerTermMap[term])
            numberOfTweetsPerThres=[0]*len(S_FOR_FILTERING)

            
            for indiceI in range(numberOfTweetOfThisTerm) :
                tweetI=tweets[tweetsOfTerm[indiceI]]
                for indiceJ in range(indiceI+1,numberOfTweetOfThisTerm) :
                    tweetJ=tweets[tweetsOfTerm[indiceJ]]
                    k=len(S_FOR_FILTERING)-1
                    distanceIJ=tweetI.distanceP(tweetJ)
                    while (k>=0 and distanceIJ<=S_FOR_FILTERING[k]) :
                        numberOfTweetsPerThres[k]+=1
                        k-=1
            LValuesPerThres=[sqrt(((2*totalArea*numPerThres)/numberOfTweetOfThisTerm)/pi)-thres for thres,numPerThres in zip(S_FOR_FILTERING,numberOfTweetsPerThres)]
            meanLValue=sum(LValuesPerThres)/len(LValuesPerThres)
            if (meanLValue<THRESHOLD_FOR_FILTERING) : termToDelete=True

        #Delete term 
        if (termToDelete) :
            tweetsOfTerm=TweetPerTermMap[term]
            for i in tweetsOfTerm :
                TFVectorI=TFVectors[i]
                del TFVectorI[term]
            del TweetPerTermMap[term]

        #Preserve Term and MAJ IDFVector value
        else :
            IDFVector[term]=log(float(numberOfTweets)/IDFVector[term],10)

    #-----------------------------------------------------------------------
    """
    print "-"*40
    print "After Filtering ..."
    print "Number of term : ", len(TweetPerTermMap)
    print "Number of non empty tweets : ",len([1 for tfv in TFVectors if len(tfv)>0])
    print "-"*40
    """
    #-----------------------------------------------------------------------

    #Construct the normalized TFIDFVectors
    TFIDFVectors=[]
    for TFVector in TFVectors :
        TFIDFVector={}
        TFIDFVectorNorm=0
        for term in TFVector :
            TFIDF=TFVector[term]*IDFVector[term]
            TFIDFVector[term]=TFIDF
            TFIDFVectorNorm+=TFIDF**2
        TFIDFVectorNorm=sqrt(TFIDFVectorNorm)
        for term in TFIDFVector :
            TFIDFVector[term]/=TFIDFVectorNorm
        TFIDFVectors.append(TFIDFVector)
            
    return TFIDFVectors,TweetPerTermMap
            
