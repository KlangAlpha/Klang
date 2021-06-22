from .klex import tokens,precedence 
from .mAST import mAST
from ply import *
import copy

DEBUG_MODE = False 

# import some required globals from tokenizer
astList = []

def p_program(p):
    'program : function'
    global astList
    debug('PROGRAM', p[1])
    p[0] = copy.copy(astList)
    astList = []

def p_function(p):
    '''
    function : function statement SEMI
             | function line_statement
             | function kloop
             | empty
    '''
    if len(p) > 2:
        debug('FUNCTION2', str(p[2]))
        astList.append(p[2])
        p[0] = p[2]
    else:
        debug('FUNCTION1', p[1:])

#存储多条语句组成的语句block
blockList=[]
def p_func_block(p):
    '''
    func_block : func_block statement SEMI
               | func_block line_statement
               | empty 
    '''
    if len(p) > 2:
        debug('FUNBLOCK', str(p[2]))
        blockList.append(p[2])
        p[0] = blockList
    else:
        debug('FUNCTION', p[1:])

#讲循环里面的语句块 加入到loop里面
def p_kloop(p):
    '''
    kloop : KLOOP SEMI func_block  ENDP %prec LOOP_INSTR
    '''
    global blockList
    p[0] = mAST(action='kloop',params=copy.copy(blockList))
    blockList = []

def p_statement_none(p):
    'line_statement : SEMI'
    debug('EMPTY STMT')


def p_statement_expr(p):
    'line_statement : expression SEMI'
    debug('STMT', p[1:])
    p[0] = p[1]


def p_statement(p):
    """
    statement : statement_print
    """
    p[0] = p[1]

def p_statement_print(p):
    'statement_print : PRINT LPAREN expr_list RPAREN'
    debug('PRINT', p[3])
    p[0] = mAST(action='print', params=p[3])

def p_statement_func(p):
    'statement_func : ID LPAREN expr_list RPAREN'
    debug('FUNC', p[3])
    p[0] = mAST(action='func', params=[p[1],p[3]])

def p_range(p):
    'range : RANGE LPAREN expr_list RPAREN'
    debug('RANGE', p[3])
    p[0] = list(range(p[3][0], p[3][1]))


def p_statement_for(p):
    'line_statement : FOR ID IN range COLON statement SEMI'
    debug('FOR', p[1:])
    p[0] = mAST(action='loop', params=[p[2], p[4], p[6]])


def p_for_stmt(p):
    'for_line_stmt : SEMI line_statement %prec LOOP_INSTR'
    p[0] = p[2]


def p_statement_for_line(p):
    '''
    line_statement : FOR ID IN range COLON line_statement
                   | FOR ID IN range COLON for_line_stmt %prec LOOP_INSTR
    '''
    debug('FOR', p[1:])
    if len(p) < 8:
        p[0] = mAST(action='loop', params=[p[2], p[4], p[6]])
    else:
        p[0] = mAST(action='loop', params=[p[2], p[4], p[7]])


def p_statement_cond_postfix_else(p):
    """
    line_statement : statement IF condition_list ELSE statement SEMI
    """
    debug("PSTFX IF-ELSE", p[1:])
    p[0] = mAST(action='condition', params=[p[3], p[1], p[5]])


def p_ifassign(p):
    'if_assign : ID ASSIGN expression'
    p[0] = [p[1], p[3]]


def p_statement_cond_postfix_assign(p):
    '''
    line_statement : if_assign IF condition_list ELSE expression SEMI
    '''
    debug("PSTFX IF-ELSE-ASSIGN", p[1:])
    p[0] = mAST(action='assign', params=[
        p[1][0], mAST(action='condition', params=[p[3], p[1][1], p[5]])
    ])


def p_statement_cond(p):
    '''
    line_statement : IF condition_list COLON statement SEMI %prec IFX
                   | IF condition_list COLON SEMI statement SEMI %prec IFX
                   | IF condition_list COLON SEMI statement_func SEMI %prec IFX
                   | IF condition_list COLON statement_func SEMI %prec IFX
                   | IF condition_list COLON SEMI ID ASSIGN condition_list SEMI %prec IFX
    '''
    debug("IF", [str(x) for x in p[1:]])
    if len(p) < 7:
        p[0] = mAST(action='condition', params=[p[2], p[4]])
    else:
        p[0] = mAST(action='condition', params=[p[2], p[5]])


def p_statement_assign_list(p):
    '''
    line_statement : idlist ASSIGN condition_list SEMI
    '''
    p[0] = mAST(action='assign_list', params=[p[1], p[3]])
    
    

def p_idlist(p):
    '''
    idlist : ID COMMA ID
           | idlist COMMA ID  
    '''
    if isinstance(p[1],list):
        p[1].append(p[3])
        p[0] = p[1]
    else :
        p[0] = [p[1],p[3]]


def p_statement_assign(p):
    '''
    line_statement : ID ASSIGN condition_list SEMI
    '''
    debug('ASSIGN', p[1], p[3])
    p[0] = mAST(action='assign', params=[p[1], p[3]])

def p_expression_list(p):
    '''
    expr_list : expression
              | expr_list COMMA expression
    '''
    debug('EXPR_LIST', p[1:])
    if len(p) <= 3:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


 


def p_condition_list(p):
    '''
    condition_list : expression 
                   
    '''

    debug('CONDITION', p[1:])
    if len(p) > 2:
        p[0] = mAST(action='logop', params=p[1:])
    else:
        p[0] = p[1]


def p_expression_func(p):
    'expression : statement_func'
    p[0] = p[1]

def p_expression_bool_true(p):
    'expression : TRUE'
    p[0] = True


def p_expression_bool_false(p):
    'expression : FALSE'
    p[0] = False


def p_expression_var(p):
    'expression : ID'
    debug('VAR', p[1])
    p[0] = mAST(action='get', params=[p[1]])

#[\d+] , C[1]
def p_expression_varslice(p):
    '''
    expression : ID LBRACKET NUMBER RBRACKET
               | ID LBRACKET REM NUMBER RBRACKET
    '''
    debug('VAR', p[1])
    if len(p) == 5:
        p[0] = mAST(action='get_slice', params=[p[1],p[3]])
    if len(p) == 6:
        p[0] = mAST(action='get_slice', params=[p[1],-int(p[4])])

def p_expression_num(p):
    'expression : NUMBER'
    debug('NUMBER', p[1])
    p[0] = int(p[1])

def p_expression_float(p):
    'expression : FLOAT'
    debug('FLOAT', p[1])
    p[0] = float(p[1])


def p_expression_string(p):
    'expression : STRING'
    debug('STRING', p[1])
    p[0] = p[1]


def p_expression_uminus(p):
    'expression : REM expression %prec NEGATE'
    debug('NEGATE', p[2])
    p[0] = mAST(action='binop', params=[-1, '*', p[2]])


def p_expression_binop(p):
    '''
    expression : expression ADD expression
               | expression REM expression
               | expression MUL expression
               | expression DIV expression
               | expression MOD expression
               | expression POW expression
               | expression GT expression
               | expression GE expression
               | expression LT expression
               | expression LE expression
               | expression EQ expression 
               | expression NE expression
               | expression AND expression
               | expression OR expression
    '''
    debug('BINOP', p[1:])
    p[0] = mAST(action='binop', params=p[1:])


def p_expression_parens(p):
    'expression : LPAREN expression RPAREN'
    debug('PARENS', p[2])
    p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!", p)


def p_empty(p):
    'empty :'
    pass


def debug(*params):
    if DEBUG_MODE:
        print("[DBG] %s" % (' : '.join(str(x) for x in params),))


#parsetab.py -->outputdir

kparser = yacc.yacc(debug=False,outputdir="/tmp")

def Kexec(datas):
    result = kparser.parse(datas)
    for x in result:
        if x is not None:
            x.run()


