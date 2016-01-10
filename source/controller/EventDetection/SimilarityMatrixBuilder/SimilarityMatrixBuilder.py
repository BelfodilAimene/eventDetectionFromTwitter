from abc import ABCMeta, abstractmethod

class SimilarityMatrixBuilder :
     __metaclass__ = ABCMeta
     @abstractmethod
     def build(self,tweets) :
          """
          input :
               tweets : list of tweet of size n
          output :
               Matrix : similarity matrix of dimension n x n
          """
          pass
