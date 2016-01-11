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
        timeResolution=self.timeResolution
        distanceResolution=self.distanceResolution
        scaleNumber=self.scaleNumber
        
        numberOfTweets=len(tweets)
        floatNumberOfTweets=float(numberOfTweets)
        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        deltaDlat=float(distanceResolution)/DEG_LATITUDE_IN_METER
        deltaDlon=float(distanceResolution)/DEG_LATITUDE_IN_METER
        print "\t\tPass 1 - Get General Information"
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
        minDistance=distanceResolution
        leftUpperCorner =Position(minLat+deltaDlat/2,minLon+deltaDlon/2)
        rightLowerCorner=Position(int(maxLat/deltaDlat)*deltaDlat+deltaDlat/2,int(maxLon/deltaDlon)*deltaDlon+deltaDlon/2)
        maxDistance=leftUpperCorner.approxDistance(rightLowerCorner)
        scalesMaxDistances=getScalesMaxDistances(minDistance,maxDistance,scaleNumber)
        temporalSeriesSize=int(2**math.ceil(math.log(int((maxTime-minTime).total_seconds()/timeResolution)+1,2)))
        haarTransformeSize=min(pow(2,scaleNumber),temporalSeriesSize)
        maximalSupportableScale=min(scaleNumber,int(math.log(haarTransformeSize,2)))

        print "\t\tPass 2 - Construct TFVectors, IDFVector, tweetsPerTermMap, timeSerieMap and cellOfTweet"
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
            timeIndex=int((tweet.time-minTime).total_seconds()/timeResolution)
            
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
        # timeSerieMap = {term : {cell : [haarTransform,[sum for each timescale],[std for each time scale]], ...}, ...}
        print "\t\tPass 1 on terms - Finalize IDFVectors and transform timeSerieMap to FinestHaarTransform of series"
        TERM_INDEX=0
        SHOW_RATE=100
        print "\t\t\tNumber of terms :",len(IDFVector)
        for term in IDFVector :
            if (TERM_INDEX%SHOW_RATE==0) : print "\t\t\t",TERM_INDEX
            TERM_INDEX+=1
            IDFVector[term]=math.log(floatNumberOfTweets/IDFVector[term],10)
            for cell, timeSerie in timeSerieMap[term].iteritems() :
                #the sum list and std list begin from 0 to scaleNumber-1 but refer to temporalScale from 1 to scaleNumber
                haarTransform,listOfSum,listOfStd=getFinestHaarTransform(timeSerie,temporalSeriesSize,scaleNumber),[0]*scaleNumber,[0]*scaleNumber
                for i in range(0,2) :
                    listOfSum[0]+=haarTransform[i]
                    listOfStd[0]+=math.pow(haarTransform[i],2)
                currentScale=1
                while currentScale<maximalSupportableScale :
                    listOfSum[currentScale]+=listOfSum[currentScale-1]
                    listOfStd[currentScale]+=listOfStd[currentScale-1]
                    for i in range(int(math.pow(2,currentScale)),int(math.pow(2,currentScale+1))) :
                        listOfSum[currentScale]+=haarTransform[i]
                        listOfStd[currentScale]+=math.pow(haarTransform[i],2)
                    currentScale+=1

                for currentScale in range(0,maximalSupportableScale) :
                    listOfStd[currentScale]=math.sqrt(math.pow(2,currentScale+1)*listOfStd[currentScale]-math.pow(listOfSum[currentScale],2))
                while currentScale<scaleNumber:
                    listOfSum[currentScale]=listOfSum[maximalSupportableScale-1]
                    listOfStd[currentScale]=listOfStd[maximalSupportableScale-1]
                    currentScale+=1

                timeSerieMap[term][cell]=[haarTransform,listOfSum,listOfStd]

        print "\t\tPass 3 - Finalize TF-IDF Vectors" 
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
        print "Constructing Similarity Matrix ..."
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

                    spatialScale=scaleNumber
                    distanceBetweetTweets=tweetI.position.approxDistance(tweetJ.position)
                    while (spatialScale>1 and distanceBetweetTweets>scalesMaxDistances[scaleNumber-spatialScale]) : spatialScale-=1
                    temporalScale=scaleNumber+1-spatialScale
                    
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
    maxSize=min(pow(2,temporalScale),len(finestHaarTransform_1[0]))
    sum1=finestHaarTransform_1[1][temporalScale-1]
    sum2=finestHaarTransform_2[1][temporalScale-1]
    std1=finestHaarTransform_1[2][temporalScale-1]
    std2=finestHaarTransform_2[2][temporalScale-1]
    if (std1==std2==0) : return 1
    if (std1*std2==0) : return 0
    prodSum=0
    for v1,v2 in zip(finestHaarTransform_1[0][0:maxSize],finestHaarTransform_2[0][0:maxSize]) : prodSum+=v1*v2
    return (maxSize*prodSum-sum1*sum2)/(std1*std2)
