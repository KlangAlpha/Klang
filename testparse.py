#test lex parse

from lang import kparser,setPY,Kexec
from Klang.common import today 
from Klang import Kl,C,MA,CROSS

#
# today 
#

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 

def getstockinfo(a):
    return Kl.currentdf['name'] + "-" + Kl.currentdf['code']

pi=3.1415926

print(C/C[1])


testblock=\
"""

kloop
ret = CROSS(MA(C,5),MA(C,10))
info = getstockinfo(0)
if ret == True:
    print(info,ret)
endp

"""

Kexec(testblock)


while True:
    # 通过Klang谁知一个变量    
    Kexec("O=pi+1;")

    s = input("Kl:>")
    if s == "quit":
        break
    
    Kexec(s+";")

#python里获取klang设置的变量值
print(O)
