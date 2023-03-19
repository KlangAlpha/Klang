#
# Klang lib
#


from .Klang import Kl,Klang_init #1.
from .Kdatas import *            #2.
from .KSeq2Feature import *      #3. 特征计算
from .tdx import *               # tdx公式算法
from .Kfeature import *

#2023.03.19
version="0.9.9"

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
    "TURN","T",
    "DATETIME",

    "WOPEN", "WO",
    "WHIGH", "WH",
    "WLOW", "WL",
    "WCLOSE", "WC",
    "WVOLUME", "WV", "WVOL",
    "WTURN","WT",
 
    "MOPEN", "MO",
    "MHIGH", "MH",
    "MLOW", "ML",
    "MCLOSE", "MC",
    "MVOLUME", "MV", "MVOL",
    "MTURN","MT",

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
    "IF", "IIF",
    "TRANSVERSE"
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

