#
# kshape 主要是编写形态结构
#
from .Kdatas import * 
from .talib_api import *
from .tdx import * 

# 波动率函数
# h 指 最高值
# l 指 最低值
# n 指 周期
# 返回 波动范围

def volatility(h1,l1,N):
    #周期不够，用当前h1周期计算
    if N > len(h1):
        N = len(h1)

    max_h = HHV(h1,N)

    min_l = LLV(l1,N)
    
    return ((max_h - min_l) / min_l ) * 100

# 横盘震荡
# 默认是 60周期
# 默认h1 是 HIGH
# 默认l1 是low
# 默认返回 波动率
# transverse

def TRANSVERSE(h1=HIGH,l1=LOW,N=60,R=None):
    r = volatility(h1,l1,N)

    # 如果没有设置震荡参数，
    # 返回波动率
    if R is None:
        return r

    # 如果设置了震荡参数
    # 返回是否是震荡
    if r <= R:
        return True
    return False
