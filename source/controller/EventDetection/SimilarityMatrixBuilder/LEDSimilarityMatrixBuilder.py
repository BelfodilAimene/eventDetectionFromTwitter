import numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from sklearn.neighbors import NearestNeighbors
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from ..Utils.TFIDFUtilities import getTweetsTFIDFVectorAndNorm
from ..Utils.Constants import DEG_LATITUDE_IN_METER

class LEDSimilarityMatrixBuilder(SimilarityMatrixBuilder) :
    def __init__(self,timeThreshold,distanceThreshold,useOnlyHashtags=False) :
        """
        timeThreshold : time threshold in seconds
        distanceThreshold : distance threshold in meter
        useOnlyHashtags : if True only hashtags will be used, if false all terms will be used
        """
        self.timeThreshold=timeThreshold
        self.distanceThreshold=distanceThreshold
        self.useOnlyHashtags=useOnlyHashtags
        
    def build(self,tweets,minimalTermPerTweet=5, remove_noise_with_poisson_Law=False) :
        """
        Return an upper sparse triangular matrix of similarity j>i
        """
        timeThreshold=float(self.timeThreshold)
        distanceThreshold=float(self.distanceThreshold)
        useOnlyHashtags=self.useOnlyHashtags
        numberOfTweets=len(tweets)

        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        print "      Calculating TF-IDF vectors ..."
        TFIDFVectors,TweetPerTermMap=getTweetsTFIDFVectorAndNorm(tweets, minimalTermPerTweet=minimalTermPerTweet, remove_noise_with_poisson_Law=remove_noise_with_poisson_Law,useOnlyHashtags=useOnlyHashtags)
        print "      Constructing similarity matrix ..."

        distanceThresholdInDegree=distanceThreshold/DEG_LATITUDE_IN_METER
        spatialIndex=NearestNeighbors(radius=distanceThresholdInDegree, algorithm='auto')
        spatialIndex.fit(np.array([(tweet.position.latitude,tweet.position.longitude) for tweet in tweets]))

        SHOW_RATE=100

        for i in range(numberOfTweets) :
            if (i%SHOW_RATE==0) : print "\t",i,";"
            
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
                similarity=0
                for term in keysIntersection : similarity+=TFIDFVectorI[term]*TFIDFVectorJ[term]
                M[i,j]=similarity

        return coo_matrix(M)
