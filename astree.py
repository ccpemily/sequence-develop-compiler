from enum import Enum


class Types(Enum):
    Int = 'int'
    Double = 'double'
    String = 'string'

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


class ASTNode(object):
    pass

class Literal(ASTNode):
    type_t:Types = None
    value = None 

    def __repr__(self):
        return '%s:%d' % (self.type_t.value, self.value)

class IdentifierRef(ASTNode):
    type_t:ComplexType = None
    name = ''

    def __repr__(self):
        return '%s' % self.name

class BinOp(ASTNode):
    ret_type:Types = None
    op = ''
    l_opd = None
    r_opd = None

class UnaryOp(ASTNode):
    ret_type:Types = None
    op = ''
    opd = None

class ArrayIndex(ASTNode):
    ret_type:ComplexType = None
    base_ref:IdentifierRef = None
    indexes = []

    def calc_ret_type(self):
        b_type = self.base_ref.type_t
        if(not b_type.is_array()):
            raise Exception("Trying to index a scalar")
        sizes = b_type.size[0:-1]
        if(len(sizes) == 0):
            self.ret_type = ComplexType(b_type.base_type)
        else:
            self.ret_type = ComplexType(b_type.base_type, sizes)

    def __repr__(self):
        return 'ArrayIndex:' + self.base_ref.name + str(self.indexes)

class Cast(ASTNode):
    ret_type = None
    opd = None

    def __repr__(self):
        return 'Cast:(%s)(%s)' % (self.ret_type.value, repr(self.opd))

class Call(ASTNode):
    type_t = None
    function_ref:IdentifierRef = None
    arg_list = []

    def __repr__(self):
        return 'Call:' + self.function_ref.name + '(' + str(self.arg_list)[1:-1] + ')'

class Assign(ASTNode):
    op = ''
    l_val = None
    r_val = None

class VarDecl(ASTNode):
    type_t = None
    identifier = None
    initializer = None

class FuncDecl(ASTNode):
    type_t = None
    identifier = None
    arg_list = []

class FuncDef(ASTNode):
    type_t = None
    identifier = None
    arg_list = []
    func_block = None
