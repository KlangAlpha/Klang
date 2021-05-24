#test lex parse

from lang import kparser,setPY
from Klang.common import today 

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

while True:
    s = input("Kl:>")
    result = kparser.parse(s+"\n")
    for x in result:
        ret = x.run()
        if ret != None:
            print(ret)
