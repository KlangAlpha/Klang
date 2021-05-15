#test lex parse

from Klang import kparser,setPY
from Klang.common import today 

#
# today 
#

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 


while True:
    s = input("Kl:>")
    result = kparser.parse(s)
    if result != None:
        print(result)
    else:
        print(a)
        break
