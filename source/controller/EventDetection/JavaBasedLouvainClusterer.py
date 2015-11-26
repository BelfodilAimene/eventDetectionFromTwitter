import numpy as np
import subprocess
import sys

class LouvainClusterer :
    def __init__(self,tweets,similarityMatrixBuilder) :
        self.tweets=tweets
        self.similarityMatrixBuilder=similarityMatrixBuilder

    def getClusters(self) :
        print "   Building similarity matrix ..."
        similarityMatrix = self.similarityMatrixBuilder.build(self.tweets)
        matrixSize=similarityMatrix.shape[0]
        
        realClusters=[]
        weightsFilePath="input.txt"
        clusterFilePath="output.txt"

        print "   Writing similarity matrix into File ..."
        # write the weights file
        
        weightsFile=open(weightsFilePath, 'w')
        maximumNodeId=0
        for i in range(matrixSize) :
            for _,j in similarityMatrix.getrow(i).keys() :
                if j>maximumNodeId :
                    maximumNodeId=j 
                line="{0}\t{1}\t{2}\n".format(i,j,similarityMatrix[i,j])
                weightsFile.write(line)
        if (maximumNodeId<matrixSize-1) :
            maximumNodeId=matrixSize-1
            line="{0}\t{1}\t{2}\n".format(maximumNodeId-1,maximumNodeId,0)
            weightsFile.write(line) 
        weightsFile.close();
        
        #np.savetxt(weightsFilePath,similarityMatrix)

        print "   Clustering ..."
        # execute the command
        command = "java -jar ModularityOptimizer.jar {0} {1} 1 0.5 2 10 10 0 0".format(weightsFilePath,clusterFilePath)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()

        print "   Reading clusters from a file ..."
        # get clusters from clusterFile (output of the command)
        with open(clusterFilePath) as f :
            realClusters=map(int,f.readlines())
            return np.array(realClusters)
            
