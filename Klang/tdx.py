#
# tdx 通达信相关的函数
#
import talib
import numpy as np

tdx_datetime=None

def settdx(d):
    global tdx_datetime

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
def CROSS(A,B):
    return A[-2] < B[-2] and A[-1] >= B[-1]


def BARSCOUNT(X):
    return len(X)

def HHV(X,N):
    if N == 0:
        data = X.data
    else:
        data = X.data[len(X)-N:]

    return talib.MAX(data,N)[-1]


def LLV(X,N):
    if N == 0:
        data = X.data
    else:
        data = X.data[len(X)-N:]
    return talib.MIN(data,N)[-1]


def iif(condition,result1,result2):
    if(condition):
        return result1
    else:
        return result2

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


"""
国内SMA算法
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
