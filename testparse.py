#test lex parse

from lang import kparser,setPY,Kexec
from Klang.common import today 
from Klang import C,MA,CROSS

#
# today 
#

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 

def testfunc(a,b=0,c=1):
    print(a,b,c,(a+b)/c)

pi=3.1415926

print(C/C[1])


testblock=\
"""
x=50
kloop
print(x)
if x>10:
    print("x>10")
if x<10:
    print("x<10")
endp;
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
