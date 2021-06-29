#test lex parse

from Klang.lang import kparser,setPY,Kexec
from Klang import (Kl,
    C,O,V,H,L, CLOSE,HIGH,
    MA,CROSS,BARSLAST,HHV,COUNT,
    MAX,MIN,MACD)


def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 

def getstockinfo(a):
    return Kl.currentdf['name'] + "-" + Kl.currentdf['code']


pi=3.1415926

#print(C/C[1])


testblock=\
"""

kloop
ret = CROSS(C,MA(C,60))
ma5 := MA(C,5)
ma10 = MA(C,10)
ma20 = MA(C,20)
ma60 = MA(C,60)

ret1 = (C - C[1])/C[1]
ret2 = (C - C[1])/C[1] > 0.05
info = getstockinfo(0)

if ma60[-1] < ma20[-1] and ma20[-1] < ma10[-1] and ma10[-1] < ma5[-1] and ret2 :
    print(info,ret1*100)

endp
print("计算完成")
"""

testblock1 =\
"""
a,b,c = MACD(C)
a = 1
e = C[1]
Kl.date('2021-01-01','2021-06-22')
"""

Kexec(testblock1)
print(a)

while True:
    # 通过Klang谁知一个变量    
    Kexec("ABCD=pi+1;")

    s = input("Kl:>")
    if s == "quit":
        break
    
    Kexec(s+";")

#python里获取klang设置的变量值
print(ABCD)
