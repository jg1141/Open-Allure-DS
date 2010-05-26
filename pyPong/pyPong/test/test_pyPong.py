from pypong import *
from nose.tools import raises, eq_

class test:
   def __init__(self,arg1=1,arg2=2):
       import utils
       utils.initFromArgs(self)

def test_initFromArgs():
    a=test()
    assert a.arg1 == 1 and a.arg2 == 2
