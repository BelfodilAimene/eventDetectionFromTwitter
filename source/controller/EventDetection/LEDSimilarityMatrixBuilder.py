import numpy as np
from scipy.sparse import dok_matrix,coo_matrix
from SimilarityMatrixBuilder import SimilarityMatrixBuilder
from TFIDFUtilities import getTweetsTFIDFVectorAndNorm

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
        M=dok_matrix((numberOfTweets, numberOfTweets),dtype=np.float)
        TFIDFVectors,TFIDFVectorsNorms=getTweetsTFIDFVectorAndNorm(tweets)
        for i in range(numberOfTweets) :
            tweetI=tweets[i]
            TFIDFVectorI=TFIDFVectors[i]
            TFIDFVectornormI=TFIDFVectorsNorms[i]
            for j in range(i+1,numberOfTweets) :
                tweetJ=tweets[j]
                if (tweetI.distance(tweetJ)<=self.distanceThreshold and tweetI.delay(tweetJ)<=self.timeThreshold) :
                    TFIDFVectorJ=TFIDFVectors[j]
                    TFIDFVectornormJ=TFIDFVectorsNorms[j]
                    similarity=0
                    for term in TFIDFVectorI :
                        if (term in TFIDFVectorJ) :
                            similarity+=TFIDFVectorI[term]*TFIDFVectorJ[term]
                    normProduct=TFIDFVectornormI*TFIDFVectornormJ
                    M[i,j]=similarity/normProduct if (normProduct>0) else 0
        return coo_matrix(M)
        

            
