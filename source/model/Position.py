import math
import numpy as np

EARTH_RADIUS=6378137

class Position :
    def __init__(self,latitude,longitude) :
        self.latitude=latitude
        self.longitude=longitude

    def distance(self,other) :
        """
        return distance between two points in earth in meter
        """
        if (self.latitude==other.latitude and self.longitude==other.longitude) : return 0
        degrees_to_radians = math.pi/180.0

        phi1 = (90.0 - self.latitude)*degrees_to_radians
        phi2 = (90.0 - other.latitude)*degrees_to_radians
         
        theta1 = self.longitude*degrees_to_radians
        theta2 = other.longitude*degrees_to_radians
         
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))

        if (cos>1) : cos=1
        elif (cos<-1) : cos=-1
    
        arc = math.acos( cos )
        return round(EARTH_RADIUS*arc,4)

    def distanceP(self,other,p=2) :
        """
        return the p-minkowski distance between the two points
        """
        return ((self.longitude-other.longitude)**p+(self.latitude-other.latitude)**p)**(1./p)

    def bearing(self,other) :
        degrees = 180 / math.pi
        dLon = other.longitude - self.longitude
        y = math.sin(dLon) * math.cos(other.latitude)
        x = math.cos(self.latitude())*math.sin(other.latitude) - math.sin(self.latitude)*math.cos(other.latitude)*math.cos(dLon)
        brng = math.atan2(y, x)*degrees
        if (brng<0) : brng+=360
        return brng

    def __str__(self) :
        return "({0},{1})".format(self.latitude,self.longitude)
