#
# tdx 通达信相关的函数
#

import numpy as np
from .Kdatas import KdataBase
import pandas as pd



tdx_datetime=None #Kdatas
kl = None         #Klang

def settdx(d,kl1):
    global tdx_datetime,kl
    kl = kl1
    tdx_datetime=d


"""
from MyTT
"""
#------------------ 0级：核心工具函数 --------------------------------------------      
def _RD(N,D=3):   return np.round(N,D)        #四舍五入取3位小数 
def _RET(S,N=1):  return np.array(S)[-N]      #返回序列倒数第N个值,默认返回最后一个
def _ABS(S):      return np.abs(S)            #返回N的绝对值
def _LN(S):       return np.log(S)            #求底是e的自然对数,
def _POW(S,N):    return np.power(S,N)        #求S的N次方
def _SQRT(S):     return np.sqrt(S)           #求S的平方根
def _MAX(S1,S2):  return np.maximum(S1,S2)    #序列max
def _MIN(S1,S2):  return np.minimum(S1,S2)    #序列min
def _IF(S,A,B):   return np.where(S,A,B)      #序列布尔判断 return=A  if S==True  else  B

def _MA(S,N):              #求序列的N日简单移动平均值，返回序列                    
    return pd.Series(S).rolling(N).mean().values  

def _DIFF(S, N=1):         #前一个值减后一个值,前面会产生nan 
    return pd.Series(S).diff(N).values     #np.diff(S)直接删除nan，会少一行

def _STD(S,N):             #求序列的N日标准差，返回序列    
    return  pd.Series(S).rolling(N).std(ddof=0).values     

def _SUM(S, N):            #对序列求N天累计和，返回序列    N=0对序列所有依次求和         
    return pd.Series(S).rolling(N).sum().values if N>0 else pd.Series(S).cumsum().values  

def _EMA(S,N):             #指数移动平均,为了精度 S>4*N  EMA至少需要120周期     alpha=2/(span+1)    
    return pd.Series(S).ewm(span=N, adjust=False).mean().values     

def _SMA(S, N, M=1):       #中国式的SMA,至少需要120周期才精确 (雪球180周期)    alpha=1/(1+com)    
    return pd.Series(S).ewm(alpha=M/N,adjust=False).mean().values           #com=N-M/M

def _WMA(S, N):            #通达信S序列的N日加权移动平均 Yn = (1*X1+2*X2+3*X3+...+n*Xn)/(1+2+3+...+Xn)
    return pd.Series(S).rolling(N).apply(lambda x:x[::-1].cumsum().sum()*2/N/(N+1),raw=True).values 

def _DMA(S, A):            #求S的动态移动平均，A作平滑因子,必须 0<A<1  (此为核心函数，非指标）
    if isinstance(A,(int,float)):  return pd.Series(S).ewm(alpha=A,adjust=False).mean().values    
    A=np.array(A);   A[np.isnan(A)]=1.0;   Y= np.zeros(len(S));   Y[0]=S[0]     
    for i in range(1,len(S)): Y[i]=A[i]*S[i]+(1-A[i])*Y[i-1]      #A支持序列 by jqz1226         
    return Y             
  
def _AVEDEV(S, N):         #平均绝对偏差  (序列与其平均值的绝对差的平均值)   
    return pd.Series(S).rolling(N).apply(lambda x: (np.abs(x - x.mean())).mean()).values 


def _HHV(S,N):             #HHV(C, 5) 最近5天收盘最高价        
    return pd.Series(S).rolling(N).max().values     

def _LLV(S,N):             #LLV(C, 5) 最近5天收盘最低价     
    return pd.Series(S).rolling(N).min().values    

#--------------------------------------------------------------------------------------



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
    if a[-2] < b[-2] and a[-1] >= b[-1]:
        return 1
    return 0

def CROSS(A,B):
    result = []
    for i in range(0,len(A)-1):
        result.insert(0,_cross(A[-i].data,B[-i].data))

    #补全最后一个
    result.insert(0,0)
    ret = KdataBase(data=result,dtype=bool)
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

    ret._data = _MAX(data,N)

    return ret


def LLV(X,N):
    ret = KdataBase()
    if N == 0:
        data = X.data
    else:
        data = X.data[len(X)-N:]
    ret._data = _MIN(data,N)

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



###########################################################

def MA(X,N):
    ret = KdataBase()
    ret._data = _MA(X.data,N)
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
    DIF = _EMA(X.data,fastperiod)-_EMA(X.data,slowperiod);  
    DEA = _EMA(DIF,signalperiod);      
    MACD= (DIF-DEA)*2

    diff,dea,macd = _RD(DIF),_RD(DEA),_RD(MACD)
    

    rdiff = KdataBase(data=diff)
    rdea = KdataBase(data=dea)
    rmacd = KdataBase(data=macd)

    return rdiff,rdea,rmacd

#RSI
def RSI(X,N=14):    
    DIF = X.data - _REF(X.data,1)
    rsi = _RD(_SMA(_MAX(DIF,0), N) / _SMA(_ABS(DIF), N) * 100)  
    rsi = KdataBase(data=rsi)
    return rsi

#BOLL
def BOLL(X,N=20,P=2):
    
    MID = pd.Series(X.data).rolling(N).mean().values; 
    UPPER = MID + _STD(X.data, N) * P
    LOWER = MID - _STD(X.data, N) * P
    upper,middle,lower = _RD(UPPER), _RD(MID), _RD(LOWER)    

    upper = KdataBase(data=upper)
    middle = KdataBase(data=middle)
    lower = KdataBase(data=lower)

    return upper,middle,lower

#KDJ
def KDJ(CLOSE,HIGH,LOW, N=9,M1=3,M2=3):           # KDJ指标
    RSV = (CLOSE.data - _LLV(LOW.data, N)) / (_HHV(HIGH.data, N) - _LLV(LOW.data, N)) * 100
    K   = _EMA(RSV, (M1*2-1));   
    D   = _EMA(K,(M2*2-1));        
    J   = K*3-D*2
    
    return KdataBase(data=K), KdataBase(data=D), KdataBase(data=J)

STOCH = KDJ 


#对X序列进行N个周期求和
#当N为0时，是求所有周期的总和
def SUM(X,N):
    ret = KdataBase()
    ret._data = _SUM(X.data,N)
    return ret

def STD(X,N):
    ret = KdataBase()
    ret._data = _STD(X.data,N)
    return ret

def EMA(X,N):
    ret = KdataBase()
    ret._data = _EMA(X.data,N)
    return ret

def WMA(X,N):
    ret = KdataBase()
    ret._data = _WMA(X.data,N)
    return ret



#######################
# Klang 自己的公式
#######################

# 返回A，B 是否接近
# 默认浮动率 0.1
# 也就是默认浮动10%为接近值
 
def APPROX(a,b,f_rate=0.1):

    if a <= b and a * (1+f_rate) >= b:
        return True

    if a >=b and  a *(1-f_rate) <= b:
        return True

    return False

