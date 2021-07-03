#
# Klang lib
#


from .Klang import Kl,Klang_init #1.
from .Kdatas import *            #2.
from .talib_api import *
from .tdx import *

#2021.07.3
version="0.2.0"

#1. kdatas set kl
setstock(Kl)

#2. init Klang
Klang_init()

#3.set to tdx
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

