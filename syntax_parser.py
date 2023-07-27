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
            ret.function_ref = p.postfix_expr
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
        ret.l_opd = p.add_expr
        ret.r_opd = p.mult_expr
        return ret
    
    @_('add_expr')
    def rel_expr(self, p):
        return p.add_expr
    @_('rel_expr ">" add_expr', 'rel_expr "<" add_expr', 'rel_expr GE add_expr', 'rel_expr LE add_expr')
    def rel_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.rel_expr
        ret.r_opd = p.add_expr
        return ret
    
    @_('rel_expr')
    def eq_expr(self, p):
        return p.rel_expr
    @_('eq_expr EQ rel_expr', 'eq_expr NE rel_expr')
    def eq_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.eq_expr
        ret.r_opd = p.rel_expr
        return ret
    
    @_('eq_expr')
    def and_expr(self, p):
        return p.eq_expr
    @_('and_expr AND eq_expr')
    def and_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.and_expr
        ret.r_opd = p.eq_expr
        return ret
    
    @_('and_expr')
    def cond_expr(self, p):
        return p.and_expr
    @_('cond_expr OR and_expr')
    def cond_expr(self, p):
        ret = BinOp()
        ret.op = p[1]
        ret.l_opd = p.cond_expr
        ret.r_opd = p.and_expr
        return ret
    
    @_('cond_expr')
    def expr(self, p):
        return p.cond_expr
    @_('unary_expr assignment_op expr')
    def expr(self, p):
        ret = Assign()
        ret.op = p[1]
        ret.l_val = p.unary_expr
        ret.r_val = p.expr
        return ret
    
    @_('PLUSEQ', 'MINUSEQ', 'MULEQ', 'DIVEQ', 'MODEQ', '"="')
    def assignment_op(self, p):
        return p[0]

    @_('type init_declarator ";"')
    def decl(self, p):
        ret = Decl()
        init_declarator = p.init_declarator
        if(isinstance(init_declarator, IdentifierRef)):
            declarator = VarDeclarator()
            declarator.identifier = init_declarator
            init_declarator = declarator
        ret.set_declarator(p.type, init_declarator)
        return ret
    
    @_('declarator')
    def init_declarator(self, p):
        return p.declarator
    @_('declarator "=" initializer')
    def init_declarator(self, p):
        if(isinstance(p.declarator, VarDeclarator) or isinstance(p.declarator, ArrayDeclarator)):
            p.declarator.initializer = p.initializer
            return p.declarator
        elif(isinstance(p.declarator, IdentifierRef)):
            ret = VarDeclarator()
            ret.identifier = p.declarator
            ret.initializer = p.initializer
            return ret
        else:
            raise Exception("Can't initialize a function or parameter with initializer")
    
    @_('INT', 'DOUBLE', 'STRING_T', 'VOID')
    def type(self, p):
        return Types.Int if p[0] == 'int' else (Types.Double if p[0] == 'double' else (Types.String if p[0] == 'string' else Types.Void))
    
    @_('IDENTIFIER')
    def declarator(self, p):
        ret = IdentifierRef()
        ret.name = p[0]
        return ret
    @_('declarator "(" param_list ")"')
    def declarator(self, p):
        ret = FuncDeclarator()
        ret.identifier = p.declarator
        ret.arg_list = p.param_list
        return ret
    @_('declarator "(" ")"')
    def declarator(self, p):
        ret = FuncDeclarator()
        ret.identifier = p.declarator
        ret.arg_list = []
        return ret
    @_('declarator "[" literal "]"')
    def declarator(self, p):
        if(isinstance(p.declarator, IdentifierRef)):
            ret = ArrayDeclarator()
            ret.identifier = p.declarator
            ret.size = [p.literal]
            return ret
        elif(isinstance(p.declarator, ArrayDeclarator)):
            p.declarator.size.append(p.literal)
            return p.declarator
        else:
            raise Exception("Array decl must after an identifier")
    @_('declarator "[" "]"')
    def declarator(self, p):
        if(isinstance(p.declarator, IdentifierRef)):
            ret = ArrayDeclarator()
            ret.identifier = p.declarator
            literal = Literal()
            literal.type_t = Types.Int
            literal.value = -1
            ret.size = [literal]
            return ret
        elif(isinstance(p.declarator, ArrayDeclarator)):
            literal = Literal()
            literal.type_t = Types.Int
            literal.value = -1
            p.declarator.size.append(literal)
            return p.declarator
        else:
            raise Exception("Array decl must after an identifier")
    
    @_('param_decl')
    def param_list(self, p):
        return [p.param_decl]
    @_('param_list "," param_decl')
    def param_list(self, p):
        p.param_list.append(p.param_decl)
        return p.param_list

    @_('type declarator')
    def param_decl(self, p):
        ret = ParamDeclarator()
        ret.type_t = p.type
        ret.set_declarator(p.declarator)
        return ret
    
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
        ret = LabeledStmt()
        ret.label = p.IDENTIFIER
        ret.stmt = p.stmt
        return ret

    @_('"{" "}"')
    def block_stmt(self, p):
        ret = BlockStmt()
        return ret
    @_('"{" stmt_list "}"')
    def block_stmt(self, p):
        ret = BlockStmt()
        ret.stmt_list = p.stmt_list
        return ret

    @_('stmt')
    def stmt_list(self, p):
        return [p.stmt]
    @_('stmt_list stmt')
    def stmt_list(self, p):
        p.stmt_list.append(p.stmt)
        return p.stmt_list

    @_('";"')
    def expr_stmt(self, p):
        return ExprStmt()
    @_('expr ";"')
    def expr_stmt(self, p):
        ret = ExprStmt()
        ret.expr = p.expr
        return ret
    @_('decl')
    def expr_stmt(self, p):
        ret = DeclStmt()
        ret.decl = p.decl
        return ret
    
    @_('IF "(" expr ")" stmt')
    def if_stmt(self, p):
        ret = IfStmt()
        ret.cond = p.expr
        ret.if_branch = p.stmt
        return ret
    @_('IF "(" expr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        ret = IfStmt()
        ret.cond = p.expr
        ret.if_branch = p[4]
        ret.else_branch = p[6]
        return ret
    
    @_('WHILE "(" expr ")" stmt')
    def loop_stmt(self, p):
        ret = WhileStmt()
        ret.cond = p.expr
        ret.stmt = p.stmt
        return ret
    @_('DO stmt WHILE "(" expr ")" ";"')
    def loop_stmt(self, p):
        ret = DoWhileStmt()
        ret.cond = p.expr
        ret.stmt = p.stmt
        return ret
    @_('FOR "(" expr_stmt expr_stmt expr ")" stmt')
    def loop_stmt(self, p):
        ret = ForStmt()
        ret.init = p[2].expr
        ret.cond = p[3].expr
        ret.action = p[4]
        ret.stmt = p[6]
        return ret
    
    @_('GOTO IDENTIFIER ";"')
    def jump_stmt(self, p):
        ret = GotoStmt()
        ret.label = p.IDENTIFIER
        return ret
    @_('CONTINUE ";"')
    def jump_stmt(self, p):
        return ContinueStmt()
    @_('BREAK ";"')
    def jump_stmt(self, p):
        return BreakStmt()
    @_('RETURN ";"')
    def jump_stmt(self, p):
        ret = ReturnStmt()
        return ret
    @_('RETURN expr ";"')
    def jump_stmt(self, p):
        ret = ReturnStmt()
        ret.returns = p.expr
        return ret
    
    @_('ext_decl')
    def translation_unit(self, p):
        return [p.ext_decl]
    @_('translation_unit ext_decl')
    def translation_unit(self, p):
        p.translation_unit.append(p.ext_decl)
        return p.translation_unit
    
    @_('decl')
    def ext_decl(self, p):
        ret = GlobalVarDecl()
        ret.decl = p.decl
        return ret
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
        ret = FuncDef()
        ret.declarator = p.declarator
        ret.set_type(p.type)
        ret.func_block = p.block_stmt
        return ret
    
    @_('INCLUDE STRING')
    def include_decl(self, p):
        ret = IncludeDecl()
        ret.includes = p.STRING
        return ret
    
    @_('DEFINE IDENTIFIER IDENTIFIER', 'DEFINE IDENTIFIER literal', 'DEFINE IDENTIFIER STRING')
    def define_decl(self, p):
        ret = DefineDecl()
        ret.symbol = p[1]
        ret.val = p[2]
        return ret
    
    @_('IMPORT IDENTIFIER INTEGER INTEGER STRING IDENTIFIER')
    def import_decl(self, p):
        ret = ImportDecl()
        ret.modules = p[1]
        ret.id_x = p[2]
        ret.id_y = p[3]
        ret.filename = p[4]
        ret.symbol = p[5]
        return ret
    
    def error(self, p):
        if(p):
            print('Syntax error at token', p.type)
            print('Position at line ' + str(p.lineno))
        else:
            print('Syntax error at EOF')
        for tok in self.tokens:
            print(tok)

