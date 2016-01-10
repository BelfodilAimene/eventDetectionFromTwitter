from Position import Position

class Event :
    def __init__(self,tweets) :
        self.tweets=sorted(tweets,key=lambda tweet : tweet.time)
        
        self.eventStartingTime=self.tweets[0].time
        self.eventEndingTime=self.tweets[0].time
        self.eventMedianTime=self.tweets[len(tweets)/2].time
        self.estimatedEventDuration=self.tweets[len(tweets)/10].delay(self.tweets[(9*len(tweets))/10])

        userIdSet=set()
        self.eventCenter=Position(0,0)
        for tweet in tweets :
            userIdSet.add(tweet.userId)
            self.eventCenter.latitude+=tweet.position.latitude
            self.eventCenter.longitude+=tweet.position.longitude
            if (tweet.time<self.eventStartingTime) :
                self.eventStartingTime=tweet.time
            elif (tweet.time>self.eventEndingTime) :
                self.eventEndingTime=tweet.time
        self.eventCenter.latitude/=len(tweets)
        self.eventCenter.longitude/=len(tweets)
        self.eventRadius=self.eventCenter.distance(tweets[0].position)
        for tweet in tweets :
            distance=self.eventCenter.distance(tweet.position)
            if (distance>self.eventRadius) :
                self.eventRadius=distance
                
        self.userNumber=len(userIdSet)
        
        self.importantHashtags=self.getImportantHashtags()

    def getImportantHashtags(self, topk=10) :
        dictHashtags={}
        for t in self.tweets :
            for h in t.hashtags :
                try : dictHashtags[h.lower()]+=1
                except KeyError : dictHashtags[h.lower()]=1
        importantHashtags=sorted(list(dictHashtags), key=lambda element : dictHashtags[element], reverse=True)[0:min(topk,len(dictHashtags))]
        return importantHashtags

    #---------------- Visualize -----------------------------------------------------------------------#
    def __str__(self) :
        NUM_DIGIT=10**2
        SEPARATOR="\t|"
        S="|"+SEPARATOR.join([str(self.eventMedianTime),
                              str(int(self.estimatedEventDuration)),
                              str(float(int(NUM_DIGIT*self.eventCenter.latitude))/NUM_DIGIT),
                              str(float(int(NUM_DIGIT*self.eventCenter.longitude))/NUM_DIGIT),
                              str(float(int(NUM_DIGIT*self.eventRadius))/NUM_DIGIT),
                              str(self.userNumber),
                              str(len(self.tweets)),
                              ",".join(self.importantHashtags)])+SEPARATOR
        return S.encode("utf-8")
    #----------------------------------------------------------------------------------------------------#
