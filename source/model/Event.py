from Position import Position

class Event :
    def __init__(self,tweets) :
        self.tweets=tweets
        userIdSet=set()
        self.eventCenter=Position(0,0)
        self.eventStartingTime=tweets[0].time
        self.eventEndingTime=tweets[0].time

        for tweet in tweets :
            userIdSet.add(tweet.userId)
            self.eventCenter.latitude=tweet.position.latitude
            self.eventCenter.longitude=tweet.position.longitude
            if (tweet.time<self.eventStartingTime) :
                self.eventStartingTime=tweet.time
            elif (tweet.time>self.eventEndingTime) :
                self.eventEndingTime=tweet.time
                
        self.eventCenter.latitude/len(tweets)
        self.eventCenter.longitude/len(tweets)

        self.userNumber=len(userIdSet)

        self.eventRadius=self.eventCenter.distance(tweets[0].position)
        for tweet in tweets :
            distance=self.eventCenter.distance(tweet.position)
            if (distance>self.eventRadius) :
                self.eventRadius=distance
                
        self.importantHashtags=self.getImportantHashtags()

    def getImportantHashtags(self) :
        dictHashtags={}
        for t in self.tweets :
            for h in t.hashtags :
                try :
                    dictHashtags[h.lower()]+=1
                except KeyError :
                    dictHashtags[h.lower()]=1
        importantHashtags=dictHashtags
        return importantHashtags
        
    def __str__(self) :
        S="Event in the circle of center {0} and radius {1}m. From {2} to {3} : \n\t - Number of users : {4}\n\t - Number of tweets {5} \n\t - They say : {6}".format(self.eventCenter,
                                                                                                                                  self.eventRadius,
                                                                                                                                  self.eventStartingTime,
                                                                                                                                  self.eventEndingTime,
                                                                                                                                  self.userNumber,
                                                                                                                                  len(self.tweets),
                                                                                                                                  "< Not implemented yet ! >")
        return S
                                                                                                                                  
                                                                                                                                  
                                                                                                                                  
