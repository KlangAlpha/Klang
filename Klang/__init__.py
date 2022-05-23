#
# Klang lib
#


from .Klang import Kl,Klang_init #1.
from .Kdatas import *            #2.
from .KSeq2Feature import *      #3. 特征计算
from .talib_api import *         # 引用talib库的 基础算法
from .tdx import *               # tdx公式算法

#2022.05.19
version="0.3.0"

#1. Kl 是全局使用的变量 
# 共享 Kl 给 kdatas 
setstock(Kl)

#2. init Klang
#Klang_init()

#3.set to tdx
# 共享给 tdx模块
settdx(DATETIME,Kl)

DATE = DATETIME

__all__ = [
    "OPEN", "O",
    "HIGH", "H",
    "LOW", "L",
    "CLOSE", "C",
    "VOLUME", "V", "VOL",
    "DATETIME",

    "SMA",
    "MA",
    "EMA",
    "WMA",

    "SUM",
    "ABS",
    "STD",

    "CROSS",
    "REF",
    "MAX",
    "MIN",
    "EVERY",
    "COUNT",
    "HHV",
    "LLV",
    "IF", "IIF"
]


################
# tdx.py
################

# REF,REFDATE,CROSS,BARSCOUNT
# HHV,LLV,MIN,MAX,
# EVERY,EXIST,SMA
# COUNT,IF,IIF
# BARSLAST

##################
# talib_api.py
##################

# MA,ABS,SUM
# STD,EMA,WMA
# MACD
# APPROX

