#test lex parse

<<<<<<< HEAD
from lang import kparser, setPY
=======
from Klang import kparser,setPY
from Klang.common import today 

#
# today 
#
>>>>>>> 40c2c156066c4338b8e05b14c515433cf17b3b50

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 

<<<<<<< HEAD
def testfunc(a,b=0,c=1):
    print(a,b,c,(a+b)/c)

while True:
    s = input("Kl:>")
    result = kparser.parse(s+"\n")
    for x in result:
        ret = x.run()
        if ret != None:
            print(ret)
=======

while True:
    s = input("Kl:>")
    result = kparser.parse(s)
    if result != None:
        print(result)
    else:
        print(a)
        break
>>>>>>> 40c2c156066c4338b8e05b14c515433cf17b3b50
