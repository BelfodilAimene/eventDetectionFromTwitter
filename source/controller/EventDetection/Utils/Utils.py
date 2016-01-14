import numpy as np
import matplotlib.pyplot as plt    
def plotTweetsApparitionInTime(tweets, granularity=3600) :
    firstTweet=min(tweets, key=lambda tweet : tweet.time)
    agg={}
    for tweet in tweets :
        index=tweet.delay(firstTweet)/granularity
        if (index in agg) : agg[index]+=1
        else : agg[index]=1
    print agg
    """
    plt.figure(1)
    plt.clf()
    plt.plot(values,distribution, '-', markerfacecolor='k',markeredgecolor='k', markersize=1)
    plt.xlabel("values")
    plt.ylabel("number")
    plt.title('Number of elements {0}'.format(numberOfElements))
    plt.show()
    """
        
        
    
    
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

def cleanFile(sourcePath,destinationPath, minimumSimilarity=0.01,numberOfTweet=50000) :
    """
    clean a similarty file to another similarity file by removing all pair for whom the similarity  <  minimumSimilarity
    """
    sourceFile=open(sourcePath, 'r')
    destinationFile=open(destinationPath, 'w')
    lastI,newI,newJ=0,0,0
    SHOW_RATE=20
    for line in sourceFile :
        liste=line.split("\t")
        newI,sim=int(liste[0]),float(liste[2])
        temp=int(liste[1])
        if (newI>lastI and newI%SHOW_RATE==0) : print newI
        lastI=newI
        if (sim<minimumSimilarity) : continue
        destinationFile.write(line)
        if (temp>newJ) : newJ=temp
    if (newJ<numberOfTweet-1) : destinationFile.write("{0}\t{1}\t{2}\n".format(numberOfTweet-2,numberOfTweet-1,0))
    sourceFile.close()
    destinationFile.close()
