import numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from TFIDFUtilities import getTweetsTFIDFVectorAndNorm,getTermOccurencesVector
from ...model.Position import Position

import math


DEG_LATITUDE_IN_METER = 111320 #1 degree in latitude is equal to 111320 m

class MEDSimilarityMatrixBuilder(SimilarityMatrixBuilder) :
    def __init__(self,timeResolution,distanceResolution,scaleNumber) :
        """
        timeResolution : define the time resolution for time series
        distanceResolution : define a cell size in meter (not exact)
        scaleNumber : nscale in the paper
        """
        self.timeResolution=timeResolution
        self.distanceResolution=distanceResolution
        self.scaleNumber=scaleNumber
        
    def build(self,tweets) :
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
        numberOfTweets=len(tweets)

        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)

        TFIDFVectors,TFIDFVectorsNorms=getTweetsTFIDFVectorAndNorm(tweets)

        TermOccurencesVector=[]
        for t in tweets : TermOccurencesVector.append(getTermOccurencesVector(t.text))

        listOfCellPerTweet,dictOfTweetIndexPerCell,scalesMaxDistances,minTime,temporalSeriesSize=self.getTweetsGridIndexes(tweets)

        """
        timeSeries is a dictionary {(term,cell) : timeSerie}} (timeSerie is seen as a dictionary {timeInstant : occurence})
        that store avery calculated Time series
        """
        finestHaarTimeSeries={}
        
        for i in range(numberOfTweets) :
            tweetI=tweets[i]
            termOccurencesI=TermOccurencesVector[i]
            cellI=listOfCellPerTweet[i]
            TFIDFVectorI=TFIDFVectors[i]
            TFIDFVectornormI=TFIDFVectorsNorms[i]
            for j in range(i+1,numberOfTweets) :
                tweetJ=tweets[j]
                cellJ=listOfCellPerTweet[j]
                TFIDFVectorJ=TFIDFVectors[j]
                TFIDFVectorJ=TFIDFVectors[j]
                TFIDFVectornormJ=TFIDFVectorsNorms[j]

                setOfCommonTerm=set(TFIDFVectorI.keys()) & set(TFIDFVectorJ.keys())
                if (setOfCommonTerm) :
                    #---------------------------------------------------------------------------
                    #  Calculate TF IDF similarity
                    #---------------------------------------------------------------------------
                    
                    STFIDF=0
                    for term in setOfCommonTerm :
                        STFIDF+=TFIDFVectorI[term]*TFIDFVectorJ[term]
                    normProduct=TFIDFVectornormI*TFIDFVectornormJ
                    STFIDF=STFIDF/normProduct

                    #---------------------------------------------------------------------------
                    #  Calculate SpatioTemporal similarity
                    #---------------------------------------------------------------------------
                    SST=None

                    spatialScale=self.scaleNumber
                    distanceBetweetTweets=tweetI.distance(tweetJ)
                    while (spatialScale>1 and distanceBetweetTweets>scalesMaxDistances[self.scaleNumber-spatialScale]) :
                        spatialScale-=1
                    temporalScale=self.scaleNumber+1-spatialScale
                    
                    for term in setOfCommonTerm :

                        try:
                           finestHaarTimeSerieOfTermAndCell_I=finestHaarTimeSeries[(term,cellI)]

                        except KeyError:
                           finestHaarTimeSerieOfTermAndCell_I=getFinestHaarTimeSerieOfTermAndCell(term,cellI,tweets,TermOccurencesVector,
                                                                                                  dictOfTweetIndexPerCell,minTime,self.timeResolution,
                                                                                                  temporalSeriesSize,self.scaleNumber)
                           finestHaarTimeSeries[(term,cellI)]=finestHaarTimeSerieOfTermAndCell_I

                        try:
                           finestHaarTimeSerieOfTermAndCell_J=finestHaarTimeSeries[(term,cellJ)]

                        except KeyError:
                           finestHaarTimeSerieOfTermAndCell_J=getFinestHaarTimeSerieOfTermAndCell(term,cellJ,tweets,TermOccurencesVector,
                                                                                                  dictOfTweetIndexPerCell,minTime,self.timeResolution,
                                                                                                  temporalSeriesSize,self.scaleNumber)
                           finestHaarTimeSeries[(term,cellJ)]=finestHaarTimeSerieOfTermAndCell_J


                        correlation=DWTBasedCorrelation(finestHaarTimeSerieOfTermAndCell_I,finestHaarTimeSerieOfTermAndCell_J,temporalScale)
                        
                        if (SST<correlation) : SST=correlation

                    #---------------------------------------------------------------------------
                    #  Calculate the similarity
                    #---------------------------------------------------------------------------
                    M[i,j]=SST*STFIDF 
        return coo_matrix(M)

    #--------------------------- Grid view of map -----------------------------------
    def getTweetsGridIndexes(self,tweets) :
        numberOfTweets=len(tweets)
        
        deltaDlat=float(self.distanceResolution)/DEG_LATITUDE_IN_METER
        deltaDlon=float(self.distanceResolution)/DEG_LATITUDE_IN_METER

        minTime=maxTime=tweets[0].time
        minLat=maxLat=tweets[0].position.latitude
        minLon=maxLon=tweets[0].position.longitude
        
        listOfCellPerTweet=[]
        dictOfTweetIndexPerCell={}

        for t in tweets :
            if (t.position.latitude<minLat) : minLat=t.position.latitude
            elif (t.position.latitude>maxLat) : maxLat=t.position.latitude

            if (t.position.longitude<minLon) : minLon=t.position.longitude
            elif (t.position.longitude>maxLon) : maxLon=t.position.longitude

            if (t.time<minTime) : minTime=t.time
            if (t.time>maxTime) : maxTime=t.time

        for k in range(numberOfTweets) :
            t=tweets[k]
            i=int((t.position.latitude-minLat)/deltaDlat)
            j=int((t.position.longitude-minLon)/deltaDlon)

            listOfCellPerTweet.append((i,j))

            try: dictOfTweetIndexPerCell[(i,j)].append(k)
            except KeyError: dictOfTweetIndexPerCell[(i,j)] = [k]
            
        leftUpperCorner=Position(minLat+deltaDlat/2,minLon+deltaDlon/2)
        rightLowerCorner=Position(int(maxLat/deltaDlat)*deltaDlat+deltaDlat/2,int(maxLon/deltaDlon)*deltaDlon+deltaDlon/2)
        maxDistance=leftUpperCorner.distance(rightLowerCorner)
        minDistance=self.distanceResolution
        scalesMaxDistances=getScalesMaxDistances(minDistance,maxDistance,self.scaleNumber)

        temporalSeriesSize=int(2**math.ceil(math.log(int((maxTime-minTime).total_seconds()/self.timeResolution)+1,2)))
        
        return listOfCellPerTweet,dictOfTweetIndexPerCell,scalesMaxDistances,minTime,temporalSeriesSize




def getScalesMaxDistances(minDistance,maxDistance,scaleNumber) :
    alpha=(maxDistance/minDistance)**(1./(scaleNumber-1))
    scalesMaxDistances=[]
    x=minDistance
    for i in range(scaleNumber) :
        scalesMaxDistances.append(x)
        x*=alpha
    return scalesMaxDistances

def getFinestHaarTimeSerieOfTermAndCell(term,cell,tweets,TermOccurencesVector,dictOfTweetIndexPerCell,minTime,timeResolution,temporalSeriesSize,scaleNumber) :
    timeSerieOfTermAndCell=getTimeSerieOfTermAndCell(term,cell,tweets,TermOccurencesVector,dictOfTweetIndexPerCell,minTime,timeResolution)
    finestHaarTransformOfTimeSerieOfTermAndCell=getFinestHaarTransform(timeSerieOfTermAndCell,temporalSeriesSize,scaleNumber)
    return finestHaarTransformOfTimeSerieOfTermAndCell

def getTimeSerieOfTermAndCell(term,cell,tweets,TermOccurencesVector,dictOfTweetIndexPerCell,minTime,timeResolution) :
    timeSerieOfTermAndCell={}
    listOfTweetIndex=dictOfTweetIndexPerCell[cell]
    for i in listOfTweetIndex :
        TermOccurencesVector_I=TermOccurencesVector[i]
        if (term in TermOccurencesVector_I) :
            timeIndex=int((tweets[i].time-minTime).total_seconds()/timeResolution)
            try: timeSerieOfTermAndCell[timeIndex]+=TermOccurencesVector_I[term]
            except KeyError: timeSerieOfTermAndCell[timeIndex]=TermOccurencesVector_I[term]           
    return timeSerieOfTermAndCell

def getFinestHaarTransform(timeSerieOfTermAndCell,temporalSeriesSize,scaleNumber) :
    haarTransform=[0]*temporalSeriesSize
    timeSeriesList=[0]*temporalSeriesSize
    size=temporalSeriesSize
    for key in timeSerieOfTermAndCell :
        timeSeriesList[key]=timeSerieOfTermAndCell[key]
    while (size>1) :
        size=size/2
        for i in range(size) :
            haarTransform[i]=float((timeSeriesList[2*i]+timeSeriesList[2*i+1]))/2
            haarTransform[i+size]=float((timeSeriesList[2*i]-timeSeriesList[2*i+1]))/2
        timeSeriesList=haarTransform[:]
    return haarTransform[0:min(pow(2,scaleNumber),temporalSeriesSize)]

def DWTBasedCorrelation(finestHaarTransform_1,finestHaarTransform_2,temporalScale) :
    maxSize=min(pow(2,temporalScale),len(finestHaarTransform_1))
    prodSum=sum1=sum2=squaresSum1=squaresSum2=0

    for i in range(maxSize) :
        sum1+=finestHaarTransform_1[i]
        sum2+=finestHaarTransform_2[i]
        prodSum+=finestHaarTransform_1[i]*finestHaarTransform_2[i]
        squaresSum1+=finestHaarTransform_1[i]**2
        squaresSum2+=finestHaarTransform_2[i]**2
    std1=math.sqrt(maxSize*squaresSum1-sum1**2)
    std2=math.sqrt(maxSize*squaresSum2-sum2**2)

    if (std1==std2==0) : return 1
    return (maxSize*prodSum-sum1*sum2)/(std1*std2) if std1*std2!=0 else 0
    
