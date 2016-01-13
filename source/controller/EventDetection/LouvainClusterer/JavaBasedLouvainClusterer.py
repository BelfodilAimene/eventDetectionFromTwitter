import sys,subprocess,numpy as np
from scipy.sparse import dok_matrix
from LouvainClusterer import LouvainClusterer

class JavaBasedLouvainClusterer(LouvainClusterer) :
    def __init__(self,tweets,similarityMatrix) :
        self.tweets=tweets
        self.similarityMatrix=similarityMatrix
        
    def getClusters(self) :
        """
        This method use ModularityOptimizer.jar
        """
       
        similarityMatrix=self.similarityMatrix
        matrixSize=similarityMatrix.shape[0]
        
        realClusters=[]
        weightsFilePath="input.txt"
        clusterFilePath="output.txt"

        # write the weights file
        print "   Writing similarity matrix into File ..."
        l=sorted(zip(similarityMatrix.row, similarityMatrix.col, similarityMatrix.data))
        if (l[-1][1]<matrixSize-1) : l.append((matrixSize-2,matrixSize-1,0))
        lines="\n".join(["{0}\t{1}\t{2}".format(i,j,v) for i,j,v in l])
        with open(weightsFilePath, 'w') as weightsFile :
            weightsFile.write(lines)
            
        return clusterFromSimilarityFile(weightsFilePath=weightsFilePath,clusterFilePath=clusterFilePath)

def clusterFromSimilarityFile(weightsFilePath="input.txt",clusterFilePath="output.txt") :
    # execute the command
    print "\tClustering ..."
    command = "java -jar ModularityOptimizer.jar {0} {1} 1 0.5 2 10 10 0 0".format(weightsFilePath,clusterFilePath)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return getClusterFromOutputFile(clusterFilePath)   
    

def getClusterFromOutputFile(clusterFilePath="input.txt") :
    # get clusters from clusterFile (output of the command)
    print "\tReading clusters from a file ..."
    with open(clusterFilePath) as f :
        realClusters=map(int,f.readlines())
        return np.array(realClusters)
    
        
        
            
