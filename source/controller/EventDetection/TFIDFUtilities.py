import numpy as np
from math import log,sqrt
import re

DELIMITERS=[",",";",":","!","\?","/","\*","=","\+","-","\."," ","\(","\)","\[","\]","\{","\}","'"]

class TFIDFUtilities :
    @staticmethod
    def getTweetsTFIDFVectorAndNorm(tweets) :
        numberOfTweets=len(tweets)
        TFVectors=[]
        IDFVector={}
        for tweet in tweets :
            TFVector=TFIDFUtilities.getTFVector(tweet.text)
            TFVectors.append(TFVector)
            for term in TFVector :
                try:
                    IDFVector[term] += 1
                except KeyError:
                    IDFVector[term] = 1

        for term in IDFVector :
            IDFVector[term]=log(float(numberOfTweets)/IDFVector[term],10)

        TFIDFVectors=[]
        TFIDFVectorsNorms=[]
        for TFVector in TFVectors :
            TFIDFVector={}
            TFIDFVectorNorm=0
            for term in TFVector :
                TFIDF=TFVector[term]*IDFVector[term]
                TFIDFVector[term]=TFIDF
                TFIDFVectorNorm+=TFIDF**2
            TFIDFVectorNorm=sqrt(TFIDFVectorNorm)
            TFIDFVectorsNorms.append(TFIDFVectorNorm)
            TFIDFVectors.append(TFIDFVector)
            
        return TFIDFVectors,TFIDFVectorsNorms
                
            

    @staticmethod
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

    @staticmethod
    def getTFVector(text) :
        TFVector={}
        terms=TFIDFUtilities.getListOfTermFromText(text)
        numberOfTerms=len(terms)
        baseFrequency=1./numberOfTerms if (numberOfTerms>0) else 0
        for term in terms :
            try:
                TFVector[term] += baseFrequency
            except KeyError:
                TFVector[term] = baseFrequency  
        return TFVector
        

            
