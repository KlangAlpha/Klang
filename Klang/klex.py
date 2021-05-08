#klang lex
from ply import *

tokens = ( 
           'ID',
           'TRUE',
           'FALSE' )

def t_TRUE(t):
    r'(true)'
    t.value = True
    return t

def t_FALSE(t):
    r'(false)'
    t.value = False
    return t

def t_ID(t):
    r'[a-zA-Z\-0-9]+'
    return t


def t_NEWLINE(t):
    r'\n+'

    t.lexer.lineno += len(t.value)
    return t

t_ignore = ' \t\n'

# Error handling rule
def t_error(t):
    print("Illegal character '{0}' at line {1}".format(t.value[0], t.lineno))
    t.lexer.skip(1)

lexer = lex.lex()
