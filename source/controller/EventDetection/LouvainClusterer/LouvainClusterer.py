from abc import ABCMeta, abstractmethod

class LouvainClusterer :
     __metaclass__ = ABCMeta
     @abstractmethod
     def getClusters(self) :
          """
          input :
               the class should have a similarity matrix and the tweets
          output :
               vector of integer giving for each tweet its cluster id
               parallel to the vector of tweets
          """
          pass
