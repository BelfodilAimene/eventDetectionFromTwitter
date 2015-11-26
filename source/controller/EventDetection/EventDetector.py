import numpy as np
from JavaBasedLouvainClusterer import LouvainClusterer
#from LouvainClusterer import LouvainClusterer
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

    def isEventImportant(self,event) :
        return (event.userNumber >= self.userNumberThreshold and len(event.tweets) >= self.tweetsNumberThreshold)
        
    #---------------- Visualize -----------------------------------------------------------------------#
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
    
    
