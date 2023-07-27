from astree import *
from sly import Parser
from scanner import Scanner

class SyntaxAnalyzer(Parser):
    tokens = Scanner.tokens

    start = 'translation_unit'

    precendence = (

    )

    debugfile = 'parser.out'

    @_('INTEGER')
    def literal(self, p):
        ret = Literal()
        ret.type_t = Types.Int
        ret.value = p.INTEGER
        return ret
    @_('FLOAT')
    def literal(self, p):
        ret = Literal()
        ret.type_t = Types.Double
        ret.value = p.FLOAT
        return ret

    # primary_expr -> IDENTIFIER
    @_('IDENTIFIER')
    def primary_expr(self, p):
        ret = IdentifierRef()
        ret.name = p.IDENTIFIER
        return ret
    @_('literal')
    def primary_expr(self, p):
        return p.literal
    # primary_expr -> (expr)
    @_('"(" expr ")"')
    def primary_expr(self, p):
        return p.expr
    
    # postfix_expr -> primary_expr
    @_('primary_expr')
    def postfix_expr(self, p):
        return p.primary_expr
    # postfix_expr -> postfix_expr[expr]
    @_('postfix_expr "[" expr "]"')
    def postfix_expr(self, p):
        if(isinstance(p.postfix_expr, ArrayIndex)):
            p.postfix_expr.indexes.append(p.expr)
            return p.postfix_expr
        else:
            ret = ArrayIndex()
            if(isinstance(p.postfix_expr, IdentifierRef)):
                ret.base_ref = p.postfix_expr
                ret.indexes = [ p.expr ]
                return ret
            else:
                raise Exception("Indexes can only apply to variable refs")
    @_('postfix_expr "(" ")"')
    def postfix_expr(self, p):
        ret = Call()
        if(isinstance(p.postfix_expr, IdentifierRef)):
            ret.function_ref = p.postdix_expr
            ret.arg_list = []
            return ret 
        else:
            raise Exception("Function call can only apply to existed func ref")
    @_('postfix_expr "(" arg_expr_list ")"')
    def postfix_expr(self, p):
        ret = Call()
        if(isinstance(p.postfix_expr, IdentifierRef)):
            ret.function_ref = p.postfix_expr
            ret.arg_list = p.arg_expr_list
            return ret 
        else:
            raise Exception("Function call can only apply to existed func ref")
    @_('postfix_expr "." IDENTIFIER')
    def postfix_expr(self, p):
        return ('member_ref', p.postfix_expr, p.IDENTIFIER)
    @_('postfix_expr INC', 'postfix_expr DEC')
    def postfix_expr(self, p):
        ret = UnaryOp()
        ret.op = p[1]
        ret.opd = p.postfix_expr
        return ret

    @_('expr')
    def arg_expr_list(self, p):
        return [p.expr]
    @_('arg_expr_list "," expr')
    def arg_expr_list(self, p):
        p.arg_expr_list.append(p.expr)
        return p.arg_expr_list

    @_('postfix_expr')
    def unary_expr(self, p):
        return p.postfix_expr
    @_('INC unary_expr', 'DEC unary_expr')
    def unary_expr(self, p):
        ret = UnaryOp()
        ret.op = p[0]
        ret.opd = p.unary_expr
        return ret
    @_('"+" cast_expr', '"-" cast_expr', '"!" cast_expr')
    def unary_expr(self, p):
        ret = UnaryOp()
        ret.op = p[0]
        ret.opd = p.unary_expr
        return ret
    
    @_('"(" type ")" cast_expr')
    def cast_expr(self, p):
        ret = Cast()
        ret.ret_type = p.type
        ret.opd = p.cast_expr
        return ret
    @_('unary_expr')
    def cast_expr(self, p):
        return p.unary_expr
    
    @_('cast_expr')
    def mult_expr(self, p):
        return p.cast_expr
    @_('mult_expr "*" cast_expr', 'mult_expr "/" cast_expr', 'mult_expr "%" cast_expr')
    def mult_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('mult_expr')
    def add_expr(self, p):
        return p.mult_expr
    @_('add_expr "+" mult_expr', 'add_expr "-" mult_expr')
    def add_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('add_expr')
    def rel_expr(self, p):
        return p.add_expr
    @_('rel_expr ">" add_expr', 'rel_expr "<" add_expr', 'rel_expr GE add_expr', 'rel_expr LE add_expr')
    def rel_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('rel_expr')
    def eq_expr(self, p):
        return p.rel_expr
    @_('eq_expr EQ rel_expr', 'eq_expr NE rel_expr')
    def eq_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('eq_expr')
    def and_expr(self, p):
        return p.eq_expr
    @_('and_expr AND eq_expr')
    def and_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('and_expr')
    def cond_expr(self, p):
        return p.and_expr
    @_('cond_expr OR and_expr')
    def cond_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('cond_expr')
    def expr(self, p):
        return p.cond_expr
    @_('unary_expr assignment_op expr')
    def expr(self, p):
        ret = Assign()
        ret.op = p[1]
        ret.l_opd = p.mult_expr
        ret.r_opd = p.cast_expr
        return ret
    
    @_('PLUSEQ', 'MINUSEQ', 'MULEQ', 'DIVEQ', 'MODEQ', '"="')
    def assignment_op(self, p):
        return p[0]

    @_('type init_declarator ";"')
    def decl(self, p):
        return ('decl', p.type, p.init_declarator[0], p.init_declarator[1])
    
    @_('declarator')
    def init_declarator(self, p):
        return (p.declarator, None)
    @_('declarator "=" initializer')
    def init_declarator(self, p):
        return (p.declarator, p.initializer)
    
    @_('INT', 'DOUBLE', 'STRING_T', 'VOID')
    def type(self, p):
        return p[0]
    
    @_('IDENTIFIER')
    def declarator(self, p):
        return p[0]
    @_('declarator "(" param_list ")"')
    def declarator(self, p):
        return ('func_decl', p.declarator, p.param_list)
    @_('declarator "(" ")"')
    def declarator(self, p):
        return ('func_decl', p.declarator, None)
    @_('declarator "[" cond_expr "]"')
    def declarator(self, p):
        return ('array_decl', p.declarator, p.cond_expr)
    @_('declarator "[" "]"')
    def declarator(self, p):
        return ('array_decl', p.declarator, None)
    
    @_('param_decl')
    def param_list(self, p):
        return [p.param_decl]
    @_('param_list "," param_decl')
    def param_list(self, p):
        p.param_list.append(p.param_decl)
        return p.param_list

    @_('type declarator')
    def param_decl(self, p):
        return ('param_decl', p.type, p.declarator)
    
    @_('expr')
    def initializer(self, p):
        return p.expr
    @_('"{" initializer_list "}"')
    def initializer(self, p):
        return p.initializer_list
    
    @_('initializer')
    def initializer_list(self, p):
        return [p.initializer]
    @_('initializer_list "," initializer')
    def initializer_list(self, p):
        p.initializer_list.append(p.initializer)
        return p.initializer_list

    @_('labeled_stmt', 'block_stmt', 'expr_stmt', 'if_stmt', 'loop_stmt', 'jump_stmt')
    def stmt(self, p):
        return p[0]
    
    @_('IDENTIFIER ":" stmt')
    def labeled_stmt(self, p):
        return ('label_stmt', p.IDENTIFIER, p.stmt)

    @_('"{" "}"')
    def block_stmt(self, p):
        return ('empty_block', None)
    @_('"{" stmt_list "}"')
    def block_stmt(self, p):
        return ('block_stmt', p[1])

    @_('stmt')
    def stmt_list(self, p):
        return [p.stmt]
    @_('stmt_list stmt')
    def stmt_list(self, p):
        p.stmt_list.append(p.stmt)
        return p.stmt_list

    @_('";"')
    def expr_stmt(self, p):
        return None
    @_('expr ";"')
    def expr_stmt(self, p):
        return ('expr_stmt', p.expr)
    @_('decl')
    def expr_stmt(self, p):
        return ('decl_stmt', p.decl)
    
    @_('IF "(" expr ")" stmt')
    def if_stmt(self, p):
        return ('if_stmt', p.expr, p.stmt, None)
    @_('IF "(" expr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        return ('if_stmt', p.expr, p[4], p[6])
    
    @_('WHILE "(" expr ")" stmt')
    def loop_stmt(self, p):
        return ('while_stmt', p.expr, p.stmt)
    @_('DO stmt WHILE "(" expr ")" ";"')
    def loop_stmt(self, p):
        return ('do_while_stmt', p.expr, p.stmt)
    @_('FOR "(" expr_stmt expr_stmt expr ")" stmt')
    def loop_stmt(self, p):
        return ('for_stmt', p[2], p[3], p[4], p[6])
    
    @_('GOTO IDENTIFIER ";"')
    def jump_stmt(self, p):
        return ('goto_stmt', p.IDENTIFIER)
    @_('CONTINUE ";"')
    def jump_stmt(self, p):
        return ('continue_stmt', None)
    @_('BREAK ";"')
    def jump_stmt(self, p):
        return ('break_stmt', None)
    @_('RETURN ";"')
    def jump_stmt(self, p):
        return ('return_stmt', None)
    @_('RETURN expr ";"')
    def jump_stmt(self, p):
        return ('return_stmt', p.expr)
    
    @_('ext_decl')
    def translation_unit(self, p):
        return [p.ext_decl]
    @_('translation_unit ext_decl')
    def translation_unit(self, p):
        p.translation_unit.append(p.ext_decl)
        return p.translation_unit
    
    @_('decl')
    def ext_decl(self, p):
        return p.decl
    @_('func_decl')
    def ext_decl(self, p):
        return p.func_decl
    @_('include_decl')
    def ext_decl(self, p):
        return p.include_decl
    @_('define_decl')
    def ext_decl(self, p):
        return p.define_decl
    @_('import_decl')
    def ext_decl(self, p):
        return p.import_decl
    
    @_('type declarator block_stmt')
    def func_decl(self, p):
        return ('func_def', p.type, p.declarator, p.block_stmt)
    
    @_('INCLUDE STRING')
    def include_decl(self, p):
        return ('include_def', p.STRING)
    
    @_('DEFINE IDENTIFIER IDENTIFIER', 'DEFINE IDENTIFIER literal', 'DEFINE IDENTIFIER STRING')
    def define_decl(self, p):
        return ('macro_def', p[1], p[2])
    
    @_('IMPORT IDENTIFIER INTEGER INTEGER STRING IDENTIFIER')
    def import_decl(self, p):
        return ('import_def', p[1], p[2], p[3], p[4], p[5])
    
    def error(self, p):
        if(p):
            print('Syntax error at token', p.type)
            print('Position at line ' + str(p.lineno))
        else:
            print('Syntax error at EOF')
        for tok in self.tokens:
            print(tok)

