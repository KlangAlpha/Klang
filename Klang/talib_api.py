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



#MACD
def MACD(X,fastperiod=12,slowperiod=26,signalperiod=9):
    diff,dea,macd = talib.MACD(X.data, fastperiod, slowperiod, signalperiod)
    macd = macd * 2

    return diff,dea,macd

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

#默认浮动率 0.1
def APPROX(A,B,f_rate=0.1):

    if a <= b and a * (1+f_rate) >= b:
        return True

    if a >=b and  a *(1-f_rate) <= b:
        return True

    return False

