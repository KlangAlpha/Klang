#test lex parse

from lang import kparser,setPY
from Klang.common import today 
from Klang import C
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

while True:
    s = input("Kl:>")
    if s == "quit":
        break
    result = kparser.parse(s+"\n")
    for x in result:
        ret = x.run()
        if ret != None:
            print(ret)
print(O)
