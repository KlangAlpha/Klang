#klang yacc
from ply import *
from .klex import tokens

getpyglobals = None
setpyglobals = None



class setPY():
    def __init__(self,getpy,setpy):
        global getpyglobals ,setpyglobals 
        getpyglobals = getpy
        setpyglobals = setpy

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)

# dictionary of names
names = {}

def p_statement_assign(p):
    'statement : NAME "=" expression'
    names[p[1]] = p[3]
    # set globals to python
    setpyglobals(p[1],p[3])

def p_statement_expr(p):
    'statement : expression'
    #print(p[1])
    p[0] = p[1]

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
    try:
        #try get globals from python
        if getpyglobals(p[1]) != None:
            p[0] = getpyglobals(p[1])
            return
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


kparser = yacc.yacc()


