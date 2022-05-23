#
# klang 解释器
# 所有语法分析后，由mAST执行

import sys
import linecache

DEBUG_MODE = False
symbols = {}


getpyglobals = None
setpyglobals = None


class setPY():
    def __init__(self,getpy,setpy):
        global getpyglobals ,setpyglobals
        getpyglobals = getpy
        setpyglobals = setpy

        setpyglobals('str',str)
        setpyglobals('int',int)
        setpyglobals('float',float)
        setpyglobals('min',min)
        setpyglobals('max',max)
        setpyglobals('len',len)

def debug(*params):
    if DEBUG_MODE:
        print("[DBG] %s" % (' : '.join(str(x) for x in params),))

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class mAST:
    action = None
    params = None

    def __init__(self, action=None, params=None):
        self.action = action
        self.params = params

    def execute(self):
        result = None
        if self.action == 'print':
            print(' '.join(str(mAST.resolve(x)) for x in list(self.params)))
        elif self.action == 'func':
            p =  [mAST.resolve(x) for x in list(self.params[1])]

            f = mAST.resolve(self.params[0])
            if isinstance(self.params[0], mAST):
                result=f(*p)
            else: 
                result=getpyglobals(f)(*p)

        elif self.action == 'assign':#存到全局变量
            result = symbols[self.params[0]] = mAST.resolve(self.params[1])
            setpyglobals(self.params[0],result)

        elif self.action == 'assign_list':#存到全局变量
            #print("params",self.params[0],self.params[1])
            l = mAST.resolve(self.params[1])
            for i in range(0,len(l)):
                result = symbols[self.params[0][i]] =l[i]
                setpyglobals(self.params[0][i],result)
            
        elif self.action == 'get':
            result = symbols.get(self.params[0], None)
            if result is None: #试着从python获取变量
                result= getpyglobals(self.params[0])

        elif self.action == 'getsub':
            result1= getpyglobals(self.params[0])
            if result1 is None:
                result = result1
            else:
                result = result1.__getattribute__(self.params[1])

        elif self.action == 'get_slice':
            ret = symbols.get(self.params[0], None)
            if ret is None: #试着从python获取变量
                ret= getpyglobals(self.params[0])

            p = mAST.resolve(self.params[1])
            result = ret[p]

        elif self.action == 'kloop':
            Kl  = getpyglobals('Kl')
            for df in Kl.df_all:
                try:
                    Kl.code(df["code"])
                    for x in self.params:
                        mAST.resolve(x)
                except :
                    print("Klang ERROR",df,Kl)
                    PrintException()

        elif self.action == 'loop':
            for i in self.params[1]:
                symbols[self.params[0]] = i
                mAST.resolve(self.params[2])
        elif self.action == 'condition':
            if mAST.resolve(self.params[0]):
                result = mAST.resolve(self.params[1])
            elif len(self.params) > 2:
                result = mAST.resolve(self.params[2])
        elif self.action == 'logop':
            params = list(self.params)
            result = mAST.resolve(params.pop())
            while len(params) >= 2:
                prev = result
                op   = mAST.resolve(params.pop()).upper()
                comp = mAST.resolve(params.pop())
                debug("[LOGOP]", prev, op, comp)
                result = {
                    'AND': lambda a, b: (a and b),
                    'OR':  lambda a, b: (a or b),
                }[op](prev, comp)

        elif self.action == 'binop':
            a = mAST.resolve(self.params[0])
            b = mAST.resolve(self.params[2])
            op = self.params[1]
            result = {
                '+':   lambda a, b: a + b,
                '-':   lambda a, b: a - b,
                '*':   lambda a, b: a * b,
                '/':   lambda a, b: a / b,
                '%':   lambda a, b: a % b,
                '**':  lambda a, b: a ** b,
                '>':   lambda a, b: (a > b),
                '>=':  lambda a, b: (a >= b),
                '<':   lambda a, b: (a < b),
                '<=':  lambda a, b: (a <= b),
                '==':  lambda a, b: (a == b),
                '!=':  lambda a, b: (a != b),
                'and': lambda a, b: (a and b),
                'or':  lambda a, b: (a or b),
            }[op](a, b)
            debug("[BINOP]", a, op, b, result)
        else:
            print("Error, unsupported operation:", str(self))

        debug('Resolving', str(self), result)
        return result

    def __str__(self):
        return '[AST] %s %s' % (self.action, ';'.join(str(x) for x in self.params))

    def run(self):
        return self.execute()

    @staticmethod
    def isADelayedAction(x=None):
        return ('x' != None and isinstance(x, mAST))

    @staticmethod
    def resolve(x):
        if not mAST.isADelayedAction(x):
            return x
        else:
            return x.execute()
