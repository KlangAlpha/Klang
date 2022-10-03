from Klang import (
    C,O,Klang,
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

print(Kl.day_df)

# 设置为茅台
code('sh.600519')
print(C)

date(start='2022-01-26',end='2022-04-29')
print(C)


#显示当天TCL的收盘价
code('sz.000100')
date()
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

code('sh.600392')

print(EVERY(C<O,2))

print(ABS(C-O))

print(EXIST(C<O,10))

