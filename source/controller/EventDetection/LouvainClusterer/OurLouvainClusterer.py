import numpy as np
from scipy.sparse import dok_matrix,coo_matrix,csr_matrix
from LouvainClusterer import LouvainClusterer

class OurLouvainClusterer(LouvainClusterer) :
    def __init__(self,tweets,similarityMatrix) :
        self.tweets=tweets
        self.similarityMatrix=similarityMatrix

    def getClusters(self) :
        PASS=1
        
        matrix=csr_matrix(self.similarityMatrixBuilder)
        continu=True
        realClusters=[]
        clusters=[]
        nextMatrix=[]
        firstRound=True
        while continu :
            print "-"*40
            print "PASS #{0}".format(PASS)
            PASS+=1
            clustersNumber,clusters=LouvainClusterer.getOnePassLouvainCommunities(matrix)
            if firstRound :
                firstRound=False
                realClusters=clusters
            else :
                LouvainClusterer.updateRealClusters(realClusters,clusters)
            if (clustersNumber==matrix.shape[0]) :
                continu=False
            else :
                nextMatrix=LouvainClusterer.buildNewSimilarityMatrix(matrix,clusters,clustersNumber)
                matrix=nextMatrix
        return np.array(realClusters)

    @staticmethod
    def updateRealClusters(realClusters,clusters) :
        for i in range(0,len(realClusters)) :
            realClusters[i]=clusters[realClusters[i]]

    @staticmethod
    def buildNewSimilarityMatrix(matrix,clusters,clustersNumber) :
        nextMatrix=dok_matrix((clustersNumber,clustersNumber),dtype=np.float)
        for i in range(0,clustersNumber) :
            for j in range(i,clustersNumber) :
                nextMatrix[i,j]=LouvainClusterer.getSimilarityOf2Clusters(matrix,clusters,i,j)
        return csr_matrix(nextMatrix)

    @staticmethod
    def getSimilarityOf2Clusters(matrix,clusters,clusterI,clusterJ) :
        iVertices=np.where(clusters == clusterI)[0]
        jVertices=np.where(clusters == clusterJ)[0]
        sumOfWeights=0
        for k in iVertices :
            for l in jVertices :
                sumOfWeights+=LouvainClusterer.getFromMatrix(matrix,k,l)
        return sumOfWeights

    @staticmethod
    def getFromMatrix(matrix,i,j) :
        return matrix[min(i,j),max(i,j)]

    @staticmethod
    def getOnePassLouvainCommunities(matrix) :
        ITER=1
        
        matrixSize=matrix.shape[0]
        sumsOfWeights=np.array([sum(matrix.getrow(i).data)+sum(matrix.getcol(i).data) for i in range(matrixSize)])
        totalSumOfWeight=sum(sumsOfWeights)
        clusters=np.array(range(0,matrixSize))
        modified=True
        while modified :
            print "  ITER #{0}".format(ITER)
            ITER+=1
            modified=False
            for i in range(0,matrixSize) :
                newCluster=LouvainClusterer.getArgMaxModularity(matrix,clusters,sumsOfWeights,totalSumOfWeight,i)
                if (newCluster!=-1) :
                    modified=True
                    clusters[i]=newCluster

        newClusterIdentifiers={}
        clustersNumber=0
        for i in range(0,len(clusters)) :
            if (clusters[i] in newClusterIdentifiers) :
                clusters[i]=newClusterIdentifiers[clusters[i]]
            else :
                newClusterIdentifiers[clusters[i]]=clustersNumber
                clusters[i]=clustersNumber
                clustersNumber+=1
        print "End of a Pass"
        print "-"*40
        return clustersNumber, clusters

    @staticmethod
    def getArgMaxModularity(matrix,clusters,sumsOfWeights,totalSumOfWeight,i) :
        """
        This function returns -1 if there is no optimization of modularity 
        """

        DMCE = LouvainClusterer.getDeltaModularityCalculElements(matrix,clusters,sumsOfWeights,totalSumOfWeight,i)
        DMCEI=DMCE[clusters[i]]
        
        maxDelta=0
        maxJ=-1

        for j in matrix.getrow(i).indices :
            delta=DMCE[clusters[j]]-DMCEI
            if (delta>maxDelta) :
                maxDelta,maxJ=delta,j

        for j in matrix.getcol(i).indices :
            delta=DMCE[clusters[j]]-DMCEI
            if (delta>maxDelta) :
                maxDelta,maxJ=delta,j
        
        if (maxDelta==0) :
            return -1

        return clusters[maxJ]

    @staticmethod
    def getDeltaModularityCalculElements(matrix,clusters,sumsOfWeights,totalSumOfWeight,i) :
        matrixSize=matrix.shape[0]
        sumOfWeightsI=sumsOfWeights[i]
        modularityPerCluster={clusters[i]:0}
        delta=0
        for k in range(i+1) :
            value=(matrix[k,i]-sumOfWeightsI*sumsOfWeights[k]/(2*totalSumOfWeight))
            try:
                modularityPerCluster[clusters[k]]+= value
            except KeyError:
                modularityPerCluster[clusters[k]] = value

        for k in range(i+1,matrixSize) :
            value=(matrix[i,k]-sumOfWeightsI*sumsOfWeights[k]/(2*totalSumOfWeight))
            try:
                modularityPerCluster[clusters[k]]+= value
            except KeyError:
                modularityPerCluster[clusters[k]] = value
        return modularityPerCluster
