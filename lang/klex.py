from re import escape
from ply.lex import TOKEN
from ply import lex

states = (
    ('string', 'inclusive'),
)

# List of basic token names.
tokens = (
    'NUMBER',
    'ID',
    'SEMI',
    'STRING',
)

reserved = {
    'print': 'PRINT',
    'range': 'RANGE',
    'if':    'IF',
    'else':  'ELSE',
    'for':   'FOR',
    'in':    'IN',
    'and':   'AND',
    'or':    'OR',
    'true':  'TRUE',
    'false': 'FALSE',
}

# List of single character literals
specials_sc = {
    '+':    'ADD',
    '-':    'REM',
    '*':    'MUL',
    '/':    'DIV',
    '%':    'MOD',
    '=':    'ASSIGN',
    '<':    'LT',
    '>':    'GT',
    '(':    'LPAREN',
    ')':    'RPAREN',
    ',':    'COMMA',
    ':':    'COLON',
}

# List of multi character literals
specials_mc = {
    '>=':  'GE',
    '<=':  'LE',
    '==':  'EQ',
    '!=':  'NE',
    '**':  'POW',
}

precedence = (
    ('nonassoc', 'LOOP_INSTR'),
    ('nonassoc', 'IFX', 'SEMI', 'FOR'),
    ('left', 'CONDLIST'),
    ('left', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
    ('left', 'REM', 'ADD'),
    ('left', 'MUL', 'DIV', 'MOD'),
    ('left', 'POW'),
    ('right', 'NEGATE'),
)

tokens = list(tokens) + list(reserved.values()) \
    + list(specials_mc.values()) + list(specials_sc.values())
specials_sc_re = '[' + escape(''.join(specials_sc.keys())) + ']'
specials_mc_re = '(' + '|'.join(escape(x) for x in specials_mc.keys()) + ')'


def t_COMMENT(t):
    r'\#.*'
    pass

#[\u4E00-\u9FA5] 简体中文
def t_ID(t):
    r'[a-zA-Z_\u4E00-\u9FA5][a-zA-Z_0-9\u4E00-\u9FA5]*'
    # Check for reserved words
    t.type = reserved.get(t.value.lower(), 'ID')
    return t


# A regular expression rule with some action code
def t_NUMBER(t):
    r'(0|[1-9]\d*)'
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_SEMI(t):
    r'\n+|;+'
    t.lexer.lineno += len(t.value)
    t.type = 'SEMI'
    # t.value = ';'
    return t


# Match the first {. Enter ccode state.
def t_STRING(t):
    r'[\"\']'
    t.lexer.begin('string')
    t.lexer.str_start = t.lexer.lexpos
    t.lexer.str_marker = t.value


def t_string_chars(t):
    r'[^"\'\n]+'


def t_string_newline(t):
    r'\n+'
    print("Incorrectly terminated string %s" % t.lexer.lexdata[t.lexer.str_start:t.lexer.lexpos - 1])
    t.lexer.skip(1)


def t_string_end(t):
    r'[\"\']'

    if t.lexer.str_marker == t.value:
        t.type = 'STRING'
        t.value = t.lexer.lexdata[t.lexer.str_start:t.lexer.lexpos - 1]
        t.lexer.begin('INITIAL')
        return t


@TOKEN(specials_mc_re)
def t_SPECIAL_MC(t):
    t.type = specials_mc.get(t.value, 'SPECIAL')
    return t


@TOKEN(specials_sc_re)
def t_SPECIAL_SC(t):
    t.type = specials_sc.get(t.value, 'SPECIAL')
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

