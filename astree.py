from enum import Enum


class Types(Enum):
    Int = 'int'
    Double = 'double'
    String = 'string'
    Void = 'void'

class DeclTypes(Enum):
    Function = 'function'
    Variable = 'variable'

class ComplexType(object):
    base_type:Types = None
    size = []
    arg_list = []

    # init a type
    def __init__(self, base_type:Types, size:list=[], arg_list:list=[]):
        self.base_type = base_type
        self.size = size.copy()
        self.arg_list = arg_list.copy()
    
    def __eq__(self, other):
        # Return type or base type not match
        if(self.base_type != other.base_type):
            return False
        elif(len(self.size) == len(other.size)):
            if(len(self.arg_list) == 0 and len(other.arg_list) == 0):
                return True # Both array, dim1 == dim2, or both scalar
            elif(len(self.arg_list) == len(other.arg_list)):
                # Both function
                for i in range(len(self.arg_list)):
                    # Argument not match
                    if(self.arg_list[i] != other.arg_list[i]):
                        return False
                return True
        return False
    
    def is_array(self):
        return len(self.size) != 0 and len(self.arg_list) == 0
    
    def is_func(self):
        return len(self.arg_list) != 0 and len(self.size) == 0
    
    def is_simple(self):
        return len(self.arg_list) == 0 and len(self.size) == 0
    
    def simplify(self) -> Types:
        if(self.is_simple()):
            return self.base_type
        else:
            raise Exception("Trying to simplify a true complex type")
        
    def __repr__(self):
        if(self.is_simple()):
            return self.simplify().value
        elif(self.is_array()):
            return self.base_type.value + '*' * len(self.size)
        elif(self.is_func()):
            args = []
            for arg in self.arg_list:
                args.append(arg)
            return '(' + str(args)[1:-1] + ') -> ' + self.base_type.value 
        
class DeclTable(object):

    pass


class ASTNode(object):
    pass

class Literal(ASTNode):
    type_t:Types = None
    value = None 

    def __repr__(self):
        return str(self.value)

class IdentifierRef(ASTNode):
    name = ''

    def __repr__(self):
        return '%s' % self.name

class BinOp(ASTNode):
    ret_type:Types = None
    op = ''
    l_opd = None
    r_opd = None

    def __repr__(self):
        l = repr(self.l_opd)
        r = repr(self.r_opd)
        if(not isinstance(self.l_opd, IdentifierRef) and not isinstance(self.l_opd, Literal) and not isinstance(self.l_opd, Call)):
            l = '(%s)' % l
        if(not isinstance(self.r_opd, IdentifierRef) and not isinstance(self.r_opd, Literal) and not isinstance(self.r_opd, Call)):
            r = '(%s)' % r
        return '%s %s %s' % (l, self.op, r)

class UnaryOp(ASTNode):
    ret_type:Types = None
    op = ''
    opd = None

    def __repr__(self):
        opd = repr(self.opd)
        if(not isinstance(self.opd, IdentifierRef) and not isinstance(self.opd, Literal) and not isinstance(self.opd, Call)):
            opd = '(%s)' % opd
        return '%s%s' % (self.op, opd)

class ArrayIndex(ASTNode):
    ret_type:ComplexType = None
    base_ref:IdentifierRef = None
    indexes = []

    def calc_ret_type(self, b_type):
        if(not b_type.is_array()):
            raise Exception("Trying to index a scalar")
        sizes = b_type.size[0:-1]
        if(len(sizes) == 0):
            self.ret_type = ComplexType(b_type.base_type)
        else:
            self.ret_type = ComplexType(b_type.base_type, sizes)

    def __repr__(self):
        return 'index:' + self.base_ref.name + str(self.indexes)

class Cast(ASTNode):
    ret_type = None
    opd = None

    def __repr__(self):
        return 'cast:(%s)(%s)' % (self.ret_type.value, repr(self.opd))

class Call(ASTNode):
    type_t = None
    function_ref:IdentifierRef = None
    arg_list = []

    def __repr__(self):
        return 'call:' + self.function_ref.name + '(' + str(self.arg_list)[1:-1] + ')'

class Assign(ASTNode):
    op = ''
    l_val = None
    r_val = None

    def __repr__(self):
        return 'assign:%s %s %s' % (repr(self.l_val), self.op, repr(self.r_val))

class Decl(ASTNode):
    type_t = None
    decl_type = None
    declarator = None

    def set_declarator(self, type_t, declarator):
        if(isinstance(declarator, VarDeclarator)):
            self.decl_type = DeclTypes.Variable
            self.declarator = declarator
            self.type_t = ComplexType(type_t)
        elif(isinstance(declarator, ArrayDeclarator)):
            self.decl_type = DeclTypes.Variable
            self.declarator = declarator
            self.type_t = ComplexType(type_t, declarator.size)
        elif(isinstance(declarator, FuncDeclarator)):
            self.decl_type = DeclTypes.Function
            self.declarator = declarator
            type_list = []
            for item in declarator.arg_list:
                type_list.append(item.type_t)
            if(len(type_list) == 0):
                type_list.append(Types.Void) 
            self.type_t = ComplexType(type_t, [], type_list)
    
    def __repr__(self):
        return 'decl:%s %s' % (repr(self.type_t), repr(self.declarator))

class GlobalVarDecl(ASTNode):
    decl = None
    
    def __repr__(self):
        return '%s;' % self.decl

class VarDeclarator(ASTNode):
    identifier = None
    initializer = None

    def __repr__(self):
        return self.identifier.name if(self.initializer == None) else ('%s = %s' % (self.identifier.name, repr(self.initializer)))

class ArrayDeclarator(ASTNode):
    identifier:IdentifierRef = None
    size:list[int] = None
    initializer = None

    def __repr__(self):
        return self.identifier.name if(self.initializer == None) else ('%s = %s' % (self.identifier.name, repr(self.initializer)))

class ParamDeclarator(ASTNode):
    identifier = None
    type_t = None

    def set_declarator(self, declarator):
        if(isinstance(declarator, VarDeclarator)):
            self.identifier = declarator.identifier
            self.type_t = ComplexType(self.type_t)
        elif(isinstance(declarator, IdentifierRef)):
            self.identifier = declarator
            self.type_t = ComplexType(self.type_t)
        elif(isinstance(declarator, ArrayDeclarator)):
            self.identifier = declarator.identifier
            self.type_t = ComplexType(self.type_t, declarator.size)
        else:
            raise Exception("Parameter can only declared as scalar or array")
        
    def __repr__(self):
        type_str = ''
        return repr(self.type_t) + ' ' + self.identifier.name

class FuncDeclarator(ASTNode):
    identifier = None
    arg_list = []

    def __repr__(self):
        return '%s(%s)' % (self.identifier, str(self.arg_list)[1:-1])

class FuncDef(ASTNode):
    type_t = None
    declarator = None
    func_block = None

    def set_type(self, type_t):
        type_list = []
        for item in self.declarator.arg_list:
            type_list.append(item.type_t)
        if(len(type_list) == 0):
            type_list.append(Types.Void)
        self.type_t = ComplexType(type_t, [], type_list)

    def __repr__(self):

        return 'funcdef:%s %s%s' % (self.type_t, self.declarator, self.func_block)
    
class LabeledStmt(ASTNode):
    label = None
    stmt = None

    def __repr__(self):
        return '%s:\n%s' % (self.label, repr(self.stmt))
    
class BlockStmt(ASTNode):
    stmt_list = []

    def __repr__(self):
        out = ''
        for stmt in self.stmt_list:
            out += repr(stmt)
        return '{\n%s}\n' % out 
    
class ExprStmt(ASTNode):
    expr = None

    def __repr__(self):
        return repr(self.expr) + ';\n'

class DeclStmt(ASTNode):
    decl = None
    def __repr__(self):
        return repr(self.decl) + ';\n'
    
class IfStmt(ASTNode):
    if_branch = None
    else_branch = None
    cond = None

    def __repr__(self):
        return ('if(%s) %s' % (repr(self.cond), repr(self.if_branch))) if self.else_branch == None else ('if(%s) %selse %s' % (repr(self.cond), repr(self.if_branch), repr(self.else_branch)))
    
class WhileStmt(ASTNode):
    stmt = None
    cond = None

    def __repr__(self):
        return 'while(%s) %s' % (repr(self.cond), repr(self.stmt))
    
class DoWhileStmt(ASTNode):
    stmt = None
    cond = None

    def __repr__(self):
        return 'do %s while(%s);\n' % (repr(self.stmt), repr(self.cond))
    
class ForStmt(ASTNode):
    init = None
    cond = None
    action = None
    stmt = None

    def __repr__(self):
        return 'for(%s;%s;%s) %s' % (repr(self.init), repr(self.cond), repr(self.action), repr(self.stmt))
    
class GotoStmt(ASTNode):
    label = None

    def __repr__(self):
        return 'goto %s;\n' % self.label
    
class ContinueStmt(ASTNode):

    def __repr__(self):
        return 'continue;\n'
    
class BreakStmt(ASTNode):

    def __repr__(self):
        return 'break;\n'
    
class ReturnStmt(ASTNode):
    returns = None

    def __repr__(self):
        return ('return %s;\n' % self.returns) if self.returns != None else 'return;'
    
class IncludeDecl(ASTNode):
    includes = None

    def __repr__(self):
        return '#include "%s"' % self.includes
    
class DefineDecl(ASTNode):
    symbol = None
    val = None

    def __repr__(self):
        return '#define %s %s' % (self.symbol, self.val)
    
class ImportDecl(ASTNode):
    modules = None
    id_x = None
    id_y = None
    filename = None
    symbol = None

    def __repr__(self):
        return 'import %s %s %s "%s" %s' % (self.modules, self.id_x, self.id_y, self.filename, self.symbol)