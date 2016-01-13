import numpy as np
import matplotlib.pyplot as plt    

def plotSimilarityDistribution(sourcePath, granularity=0.001, maxI=100) :
    """
    plot the similarity distribution of the source path (written in the same syntax used for ModularityOptimizer jar input)
    wrt. of a granularity and a maximum I (the last tweet order) 
    """
    sourceFile=open(sourcePath, 'r')
    distribution=[0]*(int(1/granularity)+1)
    values=[i*granularity for i in range(len(distribution))]
    lastI=0
    newI=0
    numberOfNeighboor=0
    numberOfElements=0
    for line in sourceFile :
        liste=line.split("\t")
        sim=float(liste[2])
        newI=int(liste[0])
        if (newI>lastI) :
            print lastI,":",numberOfNeighboor
            numberOfElements+=numberOfNeighboor
            numberOfNeighboor=0
        else : numberOfNeighboor+=1
        if (newI==maxI) : break
        distribution[int(sim/granularity)]+=1
        lastI=newI 
    sourceFile.close()
    plt.figure(1)
    plt.clf()
    plt.plot(values,distribution, '-', markerfacecolor='k',markeredgecolor='k', markersize=1)
    plt.xlabel("values")
    plt.ylabel("number")
    plt.title('Number of elements {0}'.format(numberOfElements))
    plt.show()

def cleanFile(sourcePath,destinationPath, minimumSimilarity=0.01) :
    """
    clean a similarty file to another similarity file by removing all pair for whom the similarity  <  minimumSimilarity
    """
    sourceFile=open(sourcePath, 'r')
    destinationFile=open(destinationPath, 'w')
    lastI=0
    newI=0
    for line in sourceFile :
        liste=line.split("\t")
        sim=float(liste[2])
        newI=int(liste[0])
        if (newI>lastI and newI%20==0) : print newI
        lastI=newI
        if (sim<minimumSimilarity) : continue
        destinationFile.write(line)
    sourceFile.close()
    destinationFile.close()
