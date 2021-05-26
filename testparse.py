#test lex parse

from lang import kparser,setPY
from Klang.common import today 
from Klang import C,MA
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

while True:
    # 通过Klang谁知一个变量    
    result = kparser.parse("O=pi+1;")
    for x in result:
        x.run()



    s = input("Kl:>")
    if s == "quit":
        break
    result = kparser.parse(s+"\n")
    for x in result:
        ret = x.run()
        if ret != None:
            print(ret)

#python里获取klang设置的变量值
print(O)
