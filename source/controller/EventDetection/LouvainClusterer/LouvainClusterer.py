from abc import ABCMeta, abstractmethod

class LouvainClusterer :
     __metaclass__ = ABCMeta
     @abstractmethod
     def getClusters(self) :
          """
          input :
               the class should have a similarity matrix builder and the tweets
               we construct the similarity matrix in the first step
          output :
               vector of integer giving for each tweet its cluster id
               parallel to the vector of tweets
          """
          pass
