#
# Klang lib
#


from .Klang import Kl,Klang_init
from .Kdatas import *
from .tdx import *

#kdatas set kl
setstock(Kl)

Klang_init()

settdx(
    DATETIME
)
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
