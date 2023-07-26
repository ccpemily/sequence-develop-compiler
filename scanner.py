from sly import Lexer
import re

class Scanner(Lexer):

    tokens = {
        IDENTIFIER, INTEGER, FLOAT, STRING,
        
        PLUSEQ, MINUSEQ, MULEQ, DIVEQ, MODEQ, INC, DEC,
        AND, OR, EQ, NE, GE, LE, PLUS, MINUS, MUL, DIV, NOT, ASSIGN, GT, LT, DOT, MOD,
        INCLUDE, IMPORT, DEFINE,
        INT, DOUBLE, STRING_T, VOID,
        IF, ELSE, WHILE, DO, FOR, GOTO, CONTINUE, BREAK, RETURN,
        LPARENT, RPARENT, LBRACKET, RBRACKET, LBRACE, RBRACE, COMMA, COLON, SEMICOLON
        }

    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'

    IDENTIFIER['import'] = IMPORT
    IDENTIFIER['int'] = INT
    IDENTIFIER['double'] = DOUBLE
    IDENTIFIER['string'] = STRING_T
    IDENTIFIER['void'] = VOID
    IDENTIFIER['if'] = IF
    IDENTIFIER['else'] = ELSE
    IDENTIFIER['while'] = WHILE
    IDENTIFIER['do'] = DO
    IDENTIFIER['for'] = FOR
    IDENTIFIER['goto'] = GOTO
    IDENTIFIER['continue'] = CONTINUE
    IDENTIFIER['break'] = BREAK
    IDENTIFIER['return'] = RETURN

    EQ = r'=='
    NE = r'!='
    GE = r'>='
    LE = r'<='
    PLUSEQ = r'\+='
    MINUSEQ = r'-='
    MULEQ = r'\*='
    DIVEQ = r'\/='
    MODEQ = r'%='
    AND = r'&&'
    OR = r'\|\|'
    INC = r'\+\+'
    DEC = r'--'
    LPARENT = r'\('
    RPARENT = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    LBRACE = r'{'
    RBRACE = r'}'
    COMMA = r','
    COLON = r':'
    SEMICOLON = r';'
    PLUS = r'\+'
    MINUS = r'-'
    MUL = r'\*'
    DIV = r'\\'
    NOT = r'!'
    ASSIGN = r'='
    GT = r'>'
    LT = r'<'
    DOT = r'\.'
    MOD = r'%'

    INCLUDE = r'\#include'
    DEFINE = r'\#define'

    ignore = ' \t'

    ignore_comment = r'[//].*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'[0-9]+\.[0-9]+')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'[0-9]+')
    def INTEGER(self, t):
        t.value = int(t.value)
        return t
    
    @_(r'".*"')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    def error(self, t):
        print("Line %d: Bad character %r" % (self.lineno, t.value[0]))
        self.index += 1

    def preproc(self, text:str):
        single_comment = r'[//].*[\n]'
        multi_comment = r'\/\*(?:.|\n)*\*\/'
        matches:list[str] = re.findall(multi_comment, text)
        for string in matches:
            count = string.count('\n')
            rep = '\n' * count
            text = text.replace(string, rep)
        text = re.sub(single_comment, '\n', text)
        
        return text


    def parse(self, text):
        t = self.preproc(text)
        return self.tokenize(t)