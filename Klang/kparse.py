#klang yacc
from ply import *
from .klex import tokens


def p_value(p):
    ''' value : ID
              | boolean
    '''
    p[0] = p[1]

def p_boolean(p):
    ''' boolean : TRUE
                | FALSE
    '''
    p[0] = p[1]

kparser = yacc.yacc()
