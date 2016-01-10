import numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from sklearn.neighbors import NearestNeighbors

from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ..Utils.TFIDFUtilitiesWithNoiseDetection import getTweetsTFIDFVectorAndNorm

DEG_LATITUDE_IN_METER = 111320 #1 degree in latitude is equal to 111320 m
MINIMAL_TERM_PER_TWEET=5

class LEDSimilarityMatrixBuilder(SimilarityMatrixBuilder) :
    def __init__(self,timeThreshold,distanceThreshold) :
        """
        timeThreshold : time threshold in seconds
        distanceThreshold : distance threshold in meter
        """
        self.timeThreshold=timeThreshold
        self.distanceThreshold=distanceThreshold
        
    def build(self,tweets) :
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
        numberOfTweets=len(tweets)
        #tweets=sorted(tweets,key=lambda tweet : tweet.time)
        
        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        print "      Calculating TF-IDF vectors ..."
        TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=MINIMAL_TERM_PER_TWEET, remove_noise_with_poisson_Law=False)
        print "      Constructing similarity matrix ..."

        distanceThresholdInDegree=float(self.distanceThreshold)/DEG_LATITUDE_IN_METER
        spatialIndex=NearestNeighbors(radius=distanceThresholdInDegree, algorithm='auto')
        spatialIndex.fit(np.array([(tweet.position.latitude,tweet.position.longitude) for tweet in tweets]))

        ELEMENT_NUMBER_MATRIX=0
        SHOW_RATE=100

        for i in range(numberOfTweets) :
            if (i%SHOW_RATE==0) : print i,":",ELEMENT_NUMBER_MATRIX
            
            tweetI,TFIDFVectorI=tweets[i],TFIDFVectors[i]
            neighboors=set()
            
            #Recuperation des voisins par mots (les tweets ayant au moins un term en commun)
            TFIDFVectorIKeySet=set(TFIDFVectorI)
            for term in TFIDFVectorIKeySet : neighboors|=TweetPerTermMap[term]

            #Recuperation des voisins en espace (les tweets dans le voisinage self.distanceThreshold)
            position=np.array([tweetI.position.latitude,tweetI.position.longitude]).reshape(-1,2)
            neighboors&=set(spatialIndex.radius_neighbors(position)[1][0])

            for j in neighboors :
                tweetJ=tweets[j]

                """
                Ignorer les tweets qui ne sont pas apres le tweetI
                Ignorer les tweets qui ne sont pas dans le voisinage temporelle du tweetI
                """
                if (j<=i or tweetJ.delay(tweetI)>self.timeThreshold) : continue
                
                TFIDFVectorJ=TFIDFVectors[j]
                TFIDFVectorJKeySet=set(TFIDFVectorJ)
                keysIntersection=TFIDFVectorIKeySet & TFIDFVectorJKeySet
                if (keysIntersection) :
                    ELEMENT_NUMBER_MATRIX+=1
                    similarity=0
                    for term in keysIntersection :
                        similarity+=TFIDFVectorI[term]*TFIDFVectorJ[term]
                    M[i,j]=similarity
        return coo_matrix(M)
        

            
