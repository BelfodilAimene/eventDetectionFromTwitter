import numpy as np

#from LouvainClusterer.OurLouvainClusterer import OurLouvainClusterer
from LouvainClusterer.JavaBasedLouvainClusterer import JavaBasedLouvainClusterer as LouvainClusterer
from ...model.Event import Event

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

class EventDetector :
    def __init__(self,tweets,similarityMatrixBuilder,userNumberThreshold=3,tweetsNumberThreshold=3) :
        self.tweets=np.array(tweets)
        self.similarityMatrixBuilder=similarityMatrixBuilder
        self.userNumberThreshold=userNumberThreshold
        self.tweetsNumberThreshold=tweetsNumberThreshold

    def getEvents(self) :
        print "Detecting events ..."
        louvainClusterer=LouvainClusterer(self.tweets,self.similarityMatrixBuilder)
        realClusters=louvainClusterer.getClusters()
        clustersUniqueId=set(realClusters)
        events=[]
        print "   Constructing events from clusters ..."
        for clusterId in clustersUniqueId :
            tweetsOfClusterId=self.tweets[realClusters==clusterId]
            event=Event(tweetsOfClusterId)
            if (self.isEventImportant(event)) :
                events.append(event)
        self.events=events
        return events

    #Post-processing the events
    def isEventImportant(self,event) :
        cnd1=event.userNumber >= self.userNumberThreshold and len(event.tweets) >= self.tweetsNumberThreshold
        if (not cnd1) : return False

        MAX_TOLERATED=0.5
        tweetPerUserNumber={}
        for tweet in self.tweets :
            try : tweetPerUserNumber[tweet.userId]+=1
            except KeyError : tweetPerUserNumber[tweet.userId]=1
        maximumProportionInThisEvent=float(tweetPerUserNumber[max(list(tweetPerUserNumber), key=lambda userId : tweetPerUserNumber[userId])])/len(self.tweets)
        cnd2=(maximumProportionInThisEvent<MAX_TOLERATED)
        return cnd2
        
    #---------------- Visualize -----------------------------------------------------------------------#
    def showTopKEvents(self,topk=10) :
        if not self.events :
            "No events detected !"
            return
        SIZE_OF_LINE=40
        topKEvents=sorted(self.events,key=lambda event : len(event.tweets),reverse=True)[0:min(max(1,topk),len(self.events))]
        #print "-"*SIZE_OF_LINE
        print self.events[0].getHeader()
        #print "-"*SIZE_OF_LINE 
        for event in topKEvents :
            print event
            #print "-"*SIZE_OF_LINE

    def drawEvents(self) :
        events=self.events
        m = Basemap(width=1200000,height=1200000,projection='lcc',resolution='c',lat_0=46,lon_0=3.)

        m.drawcoastlines()
        m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='white',lake_color='aqua')
        m.drawcountries()

        for event in events :
            xpt,ypt = m(event.eventCenter.longitude,event.eventCenter.latitude)
            m.plot(xpt,ypt,'bo')
            
        #m.bluemarble()
        plt.show()
    #----------------------------------------------------------------------------------------------------#
    
    
