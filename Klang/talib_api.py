#
# Ta-lib
# 本模块 talib的部分,主要是基础算法

import talib
import numpy as np
from .Kdatas import KdataBase

def MA(X,N):
    ret = KdataBase()
    ret._data = talib.MA(X.data,N)
    return ret

def ABS(X):
    ret = KdataBase()
    if isinstance(X,KdataBase):
        data = X.data
    else:
        data = X
    ret._data = np.abs(data)
    return ret


#MACD
def MACD(X,fastperiod=12,slowperiod=26,signalperiod=9):
    diff,dea,macd = talib.MACD(X.data, fastperiod, slowperiod, signalperiod)
    macd = macd * 2

    rdiff = KdataBase(data=diff)
    rdea = KdataBase(data=dea)
    rmacd = KdataBase(data=macd)

    return rdiff,rdea,rmacd

#对X序列进行N个周期求和
#当N为0时，是求所有周期的总和
def SUM(X,N):
    ret = KdataBase()
    ret._data = talib.SUM(X.data,N)
    return ret

def STD(X,N):
    ret = KdataBase()
    ret._data = talib.STDDEV(X.data,N)
    return ret

def EMA(X,N):
    ret = KdataBase()
    ret._data = talib.EMA(X.data,N)
    return ret

def WMA(X,N):
    ret = KdataBase()
    ret._data = talib.WMA(X.data,N)
    return ret

#######################
# Klang 自己的公式
#######################

# 返回A，B 是否接近
# 默认浮动率 0.1
# 也就是默认浮动10%为接近值
 
def APPROX(A,B,f_rate=0.1):

    if a <= b and a * (1+f_rate) >= b:
        return True

    if a >=b and  a *(1-f_rate) <= b:
        return True

    return False

