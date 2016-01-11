import math,re,numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ....model.Position import Position

DELIMITERS=[",",";",":","!","\?","/","\*","=","\+","-","\."," ","\(","\)","\[","\]","\{","\}","'"]
TERM_MINIMAL_SIZE=2
TERM_MAXIMAL_SIZE=31

#1 degree in latitude is equal to 111320 m
DEG_LATITUDE_IN_METER = 111320

class MEDSimilarityMatrixBuilder2(SimilarityMatrixBuilder) :
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
        floatNumberOfTweets=float(numberOfTweets)
        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        deltaDlat=float(self.distanceResolution)/DEG_LATITUDE_IN_METER
        deltaDlon=float(self.distanceResolution)/DEG_LATITUDE_IN_METER

        #Pass 1 - Get General Information
        minTime=maxTime=tweets[0].time
        minLat=maxLat=tweets[0].position.latitude
        minLon=maxLon=tweets[0].position.longitude
        for tweet in tweets :
            if (tweet.position.latitude<minLat) : minLat=tweet.position.latitude
            elif (tweet.position.latitude>maxLat) : maxLat=tweet.position.latitude
            if (tweet.position.longitude<minLon) : minLon=tweet.position.longitude
            elif (tweet.position.longitude>maxLon) : maxLon=tweet.position.longitude
            if (tweet.time<minTime) : minTime=tweet.time
            if (tweet.time>maxTime) : maxTime=tweet.time
        minDistance=self.distanceResolution
        leftUpperCorner =Position(minLat+deltaDlat/2,minLon+deltaDlon/2)
        rightLowerCorner=Position(int(maxLat/deltaDlat)*deltaDlat+deltaDlat/2,int(maxLon/deltaDlon)*deltaDlon+deltaDlon/2)
        maxDistance=leftUpperCorner.approxDistance(rightLowerCorner)
        scalesMaxDistances=getScalesMaxDistances(minDistance,maxDistance,self.scaleNumber)
        temporalSeriesSize=int(2**math.ceil(math.log(int((maxTime-minTime).total_seconds()/self.timeResolution)+1,2)))

        #Pass 2 - Construct TFVectors, IDFVector, tweetsPerTermMap, timeSerieMap and cellOfTweet
        TFIDFVectors=[]
        IDFVector={}
        tweetsPerTermMap={}
        timeSerieMap={}
        cellOfTweet=[]
        tweetIndex=0
        for tweet in tweets :
            TFVector={}
            text=tweet.text
            cell=(int((tweet.position.latitude-minLat)/deltaDlat),int((tweet.position.longitude-minLon)/deltaDlon))
            cellOfTweet.append(cell)
            timeIndex=int((tweet.time-minTime).total_seconds()/self.timeResolution)
            
            #Prepare the text
            text = text.lower()
            text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',text)
            text = re.sub('@[^\s]+','',text)
            text = re.sub('[\s]+', ' ', text)
            text = text.strip('\'"')
            regex="|".join(DELIMITERS)
            terms=re.split(regex,text)

            #Construct the Occurence vector
            for term in terms :
                if (TERM_MINIMAL_SIZE<len(term)<TERM_MAXIMAL_SIZE) :
                    try: TFVector[term] += 1
                    except KeyError: TFVector[term] = 1

            #Finalize the TF vector while constructing the IDF vector, tweetsPerTermMap and the timeSerieMap
            for term,occurence in TFVector.iteritems() :
                if term in IDFVector :
                    IDFVector[term] += 1
                    tweetsPerTermMap[term].add(tweetIndex)
                    if cell in timeSerieMap[term] :
                        try : timeSerieMap[term][cell][timeIndex]+=occurence
                        except KeyError : timeSerieMap[term][cell][timeIndex]=occurence
                    else : timeSerieMap[term][cell]={timeIndex:occurence}     
                else :
                    IDFVector[term] = 1
                    tweetsPerTermMap[term] = set([tweetIndex])
                    timeSerieMap[term]={cell:{timeIndex:occurence}}
                TFVector[term]/=floatNumberOfTweets

            TFIDFVectors.append(TFVector)
            tweetIndex+=1

        #Pass 1 on terms - Finalize IDFVectors and transform timeSerieMap to FinestHaarTransform of series
        for term in IDFVector :
            IDFVector[term]=math.log(floatNumberOfTweets/IDFVector[term],10)
            for cell, timeSerie in timeSerieMap[term].iteritems() :
                timeSerieMap[term][cell]=getFinestHaarTransform(timeSerie,temporalSeriesSize,self.scaleNumber)

        #Pass 3 - Finalize TF-IDF Vectors
        for TFIDFVector in TFIDFVectors :
            TFIDFVectorNorm=0
            for term in TFIDFVector :
                TFIDFVector[term]*=IDFVector[term]
                TFIDFVectorNorm+=math.pow(TFIDFVector[term],2)
            TFIDFVectorNorm=math.sqrt(TFIDFVectorNorm)
            for term in TFIDFVector : TFIDFVector[term]/=TFIDFVectorNorm

        #Done with preparation : TFIDFVectors, tweetsPerTermMap, timeSerieMap
        #Now is the time to construct the similarity matrix

        SHOW_RATE=1
        for i in range(numberOfTweets) :
            if (i%SHOW_RATE==0) : print i
            
            tweetI,TFIDFVectorI,cellI=tweets[i],TFIDFVectors[i],cellOfTweet[i]
            TFIDFVectorIKeySet=set(TFIDFVectorI)

            neighboors=set()

            #Recuperation des voisins par mots (les tweets ayant au moins un term en commun)
            for term in TFIDFVectorIKeySet : neighboors|=tweetsPerTermMap[term]

            for j in neighboors :
                #Ignorer les tweets qui ne sont pas apres le tweetI
                if (j<=i) : continue
                tweetJ,TFIDFVectorJ,cellJ=tweets[j],TFIDFVectors[j],cellOfTweet[j]
                TFIDFVectorJKeySet=set(TFIDFVectorJ)

                keysIntersection=TFIDFVectorIKeySet & TFIDFVectorJKeySet
                if (keysIntersection) :
                    #---------------------------------------------------------------------------
                    #  Calculate TF IDF similarity
                    #---------------------------------------------------------------------------
                    
                    STFIDF=0
                    for term in keysIntersection :
                        STFIDF+=TFIDFVectorI[term]*TFIDFVectorJ[term]

                    #---------------------------------------------------------------------------
                    #  Calculate SpatioTemporal similarity
                    #---------------------------------------------------------------------------

                    SST=None

                    spatialScale=self.scaleNumber
                    distanceBetweetTweets=tweetI.position.approxDistance(tweetJ.position)
                    while (spatialScale>1 and distanceBetweetTweets>scalesMaxDistances[self.scaleNumber-spatialScale]) : spatialScale-=1
                    temporalScale=self.scaleNumber+1-spatialScale
                    
                    for term in keysIntersection :
                        correlation=DWTBasedCorrelation(timeSerieMap[term][cellI],timeSerieMap[term][cellJ],temporalScale)
                        if (SST<correlation) : SST=correlation

                    #---------------------------------------------------------------------------
                    #  Calculate the similarity
                    #---------------------------------------------------------------------------
                    if (SST>0) : M[i,j]=SST*STFIDF
                    
        return coo_matrix(M)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#    Basic function to get the different scale of distance between minDistance anb maxDistance
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def getScalesMaxDistances(minDistance,maxDistance,scaleNumber) :
    alpha=(maxDistance/minDistance)**(1./(scaleNumber-1))
    scalesMaxDistances=[]
    x=minDistance
    for i in range(scaleNumber) :
        scalesMaxDistances.append(x)
        x*=alpha
    return scalesMaxDistances

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#    Haar Transformation
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def getFinestHaarTransform(timeSerieOfTermAndCell,temporalSeriesSize,scaleNumber) :
    haarTransform=[0]*temporalSeriesSize
    timeSeriesList=[0]*temporalSeriesSize
    size=temporalSeriesSize
    for key in timeSerieOfTermAndCell : timeSeriesList[key]=timeSerieOfTermAndCell[key]
    while (size>1) :
        size=size/2
        for i in range(size) :
            haarTransform[i]=float((timeSeriesList[2*i]+timeSeriesList[2*i+1]))/2
            haarTransform[i+size]=float((timeSeriesList[2*i]-timeSeriesList[2*i+1]))/2
        timeSeriesList=haarTransform[:]
    return haarTransform[0:min(pow(2,scaleNumber),temporalSeriesSize)]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#    DTW Correlation (for SST)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

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
