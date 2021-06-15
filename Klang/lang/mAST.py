DEBUG_MODE = False
symbols = {}


getpyglobals = None
setpyglobals = None


class setPY():
    def __init__(self,getpy,setpy):
        global getpyglobals ,setpyglobals
        getpyglobals = getpy
        setpyglobals = setpy

def debug(*params):
    if DEBUG_MODE:
        print("[DBG] %s" % (' : '.join(str(x) for x in params),))


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
            result=getpyglobals(self.params[0])(*p)

        elif self.action == 'assign':#存到全局变量
            result = symbols[self.params[0]] = mAST.resolve(self.params[1])
            setpyglobals(self.params[0],result)

        elif self.action == 'get':
            result = symbols.get(self.params[0], None)
            if result == None: #试着从python获取变量
                result= getpyglobals(self.params[0])
        elif self.action == 'get_slice':
            ret = symbols.get(self.params[0], None)
            if ret is None: #试着从python获取变量
                ret= getpyglobals(self.params[0])
            result = ret[self.params[1]]

        elif self.action == 'kloop':
            Kl  = getpyglobals('Kl')
            for df in Kl.df_all:
                try:
                    Kl.setcurrent(df["code"])

                    for x in self.params:
                        mAST.resolve(x)
                except:
                    pass

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
