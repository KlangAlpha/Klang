from Klang import (
    C,O,Klang,
    REF,REFDATE,
    MA,
    SMA,
    HHV,LLV,
    DATE,
    EVERY, EXIST
)

Kl = Klang.Kl
# 设置为隆基
Kl.setcurrent('sh.601012')
print(C)

# 设置为茅台
Kl.setcurrent('sh.600519')
print(C)

Kl.setdate(start='2021-04-26',end='2021-04-29')
print(C)


#显示当天TCL的收盘价
Kl.setcurrent('sz.000100')
Kl.setdate()
print(C)


# 系列比，可以计算出每天的涨幅
print(C.data,C[1].data)
print(C/C[1])


print(REF(C,1))
print(REFDATE(C,'20210429'))

print(MA(C,5))
print(SMA(C,5,1))
print(HHV(C,10))
print(LLV(C,10))
print(EVERY(C<O,10))

Kl.setcurrent('sh.600392')

print(EVERY(C<O,2))


print(EXIST(C<O,10))

