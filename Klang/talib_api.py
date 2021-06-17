#
# Ta-lib
#

import talib
import numpy as np
from .Kdatas import Kdatas,KdatasOpt

def MA(X,N):
    return talib.MA(X.data,N)

def ABS(X):
    if isinstance(X,Kdatas):
        data = X.data
    else:
        data = X
    return np.abs(data)

#对X序列进行N个周期求和
#当N为0时，是求所有周期的总和
def SUM(X,N):
    return talib.SUM(X.data,N)

def STD(X,N):
    return talib.STDDEV(X.data,N)

def EMA(X,N):
    return talib.EMA(X.data,N)

def WMA(X,N):
    return talib.WMA(X.data,N)
