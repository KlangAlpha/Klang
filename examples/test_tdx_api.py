import sys
from pathlib import Path # if you haven't already done so
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))


from Klang import (
    C,O,Klang,
    MC,WC,MO,WO,T,WT,MT,
    REF,REFDATE,
    MA,
    SMA,
    HHV,LLV,
    DATE,
    ABS,
    EVERY, EXIST
)

Klang.Klang_init()

Kl = Klang.Kl

code = Kl.code
date = Kl.date

# 设置为隆基
code('sh.601012')
print(C)

print(EXIST(C<O,10))
print(WC,MC,T,MT[-2],WT[-2])

from Klang import BARSLASTCOUNT

print("BARSLASTCOUNT",BARSLASTCOUNT(C>O).data)
