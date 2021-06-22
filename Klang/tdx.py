#
# tdx 通达信相关的函数
#
import talib
import numpy as np
from .Kdatas import KdataBase

tdx_datetime=None #Kdatas
kl = None         #Klang

def settdx(d,kl1):
    global tdx_datetime,kl
    kl = kl1
    tdx_datetime=d

"""
返回无效数。
用法： DRAWNULL
"""
def DNULL():
    return None

DRAWNULL = DNULL()

"""
REF 向前引用
引用若干周期前的数据。
用法：　REF(X，A)　引用A周期前的X值。
例如：　REF(CLOSE，1)　表示上一周期的收盘价，在日线上就是昨收。
"""
def REF(X,A):
    return X[A]


"""
引用指定日期的数据。
用法：　REFDATE(X，A)　引用A日期的X值。
例如：　REFDATE(CLOSE，20011208)　表示2001年12月08日的收盘价。
"""
def REFDATE(X,A):
    idx = ""
    for i in range(0,len(tdx_datetime)):
        if str(tdx_datetime[i]).replace("-","") == A:
            idx = i
            break

    if idx == "":
        return None
    return X[idx]

"""
两条线交叉。

用法：　CROSS(A，B)　表示当A从下方向上穿过B时返回1，否则返回0。

例如：　CROSS(MA(CLOSE，5)，MA(CLOSE，10))　表示5日均线与10日均线交金叉。
"""
def _cross(a,b):
    return a[-2] < b[-2] and a[-1] >= b[-1]

def CROSS(A,B):
    result = []
    for i in range(0,len(A)-1):
        result.insert(0,_cross(A[-i].data,B[-i].data))
    
    ret = KdataBase(data=result)
    return ret

def BARSCOUNT(X):
    return len(X)



"""
功能：上一次条件成立位置


描述：上一次条件成立到当前的周期数。

用法：BARSLAST(X);

例如：BARSLAST(CLOSE>OPEN);
表示上次K线收阳到当前的周期数。
"""
def BARSLAST(X):
    for i in range(0,len(X)):
        if X[i]:
            break
    return i
#
def BARSLASTFIND(X,val):
    for i in range(0,len(X)):
        if X[i] == val:
            break
    return i
#

def HHV(X,N):
    ret = KdataBase()
    if N == 0:
        data = X.data
    else:
        data = X.data[len(X)-N:]

    ret._data = talib.MAX(data,N)

    return ret


def LLV(X,N):
    ret = KdataBase()
    if N == 0:
        data = X.data
    else:
        data = X.data[len(X)-N:]
    ret._data = talib.MIN(data,N)

    return ret


def IIF(condition,result1,result2):
    if(condition):
        return result1
    else:
        return result2

IF=IIF

# 返回A和B的最小值
def MIN(A,B):
    if A < B :
        return A
    return B

# 返回A和B的最大值
def MAX(A,B):
    if A > B:
        return A
    return B

# condition is np.array
# N 周期内 一直满足条件
# EVERY(C>O,10),10个周期内一直是收阳线
def EVERY(condition,N):

    if N > len(condition):
        return False


    for i in range(0,N):
        if not condition[i]:
            return False

    return True


#N 周期内满足过某个条件
def EXIST(condition,N):
    l = min(len(condition),N)  
    
    for i in range(0,l):
        if condition[i]:
            return True

    return False

"""
类型：引用函数

功能：统计


描述：统计满足条件的周期数。
"""

def COUNT(condition,N):

    if N > len(condition):
        return 0
    if N < 0:
        N = len(condition)

    count = 0
    for i in range(0,N):
        if condition[i]:
            count += 1

    return count

    
"""
国内SMA算法,和TA-lib算法不同
"""
def SMA(datas,period,period2):
    y1 = 0
    result = []
    for d in datas:
        if str(d) == 'nan':
            result.append(np.nan)
            continue
        y1=(d * period2 + (period-period2)*y1 )/period
        result.append(y1)
    return np.array(result,dtype='float64')
