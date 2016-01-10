class Tweet :
    def __init__(self,_id,userId,text,hashtags,time,position=None) :
        self.id=_id
        self.userId=userId
        self.text=text
        self.hashtags=hashtags
        self.time=time
        self.position=position

    def delay(self,other) :
        return abs((self.time-other.time).total_seconds())

    def distance(self,other) :
        if (self.position and other.position) :
            return self.position.distance(other.position)
        else :
            return None

    def distanceP(self,other) :
        if (self.position and other.position) :
            return self.position.distanceP(other.position)
        else :
            return None
    
    def __str__(self) :
        return "{0} : ({1},{2})".format(self.id,self.time,self.position)
