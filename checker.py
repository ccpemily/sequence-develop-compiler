from astree import *
from exceptions.semantic_exceptions import *

class Variable(object):
    type_t = ComplexType(Types.Void)
    name = ''
    initialized = False

    def __init__(self, name:str, type_t:ComplexType, has_initializer:bool):
        self.name = name
        self.type_t = type_t
        self.initialized = has_initializer
    
    def initialize(self):
        self.initialized = True


class Function(object):
    type_t = ComplexType(Types.Void, [], [])
    param_list = []
    name = ''
    defined = False

    def __init__(self, name:str, type_t:ComplexType, param_list:list, is_def:bool):
        self.name = name
        self.type_t = type_t
        self.defined = self.defined or is_def
        if(not type_t.is_func()):
            raise Exception("Illegal type of function: %s" % repr(type_t))
        for para in param_list:
            self.param_list.append(para.type_t)

    def ret_type(self):
        return self.type_t.base_type


class ASTChecker(object):

    var_table:list[dict[str, Variable]] = []
    func_table:dict[str, list[Function]] = {}
    is_in_loop = False

    def __init__(self):
        pass

    def current_vars(self) -> dict[str, Variable]:
        return self.var_table[-1]
    
    def enter_scope(self) -> None:
        self.var_table.append({})

    def leave_scope(self) -> None:
        self.var_table.pop()

    def declare_variable(self, name:str, type_t:ComplexType, initializer:bool) -> bool:
        if self.current_vars().__contains__(name):
            return False
        else:
            self.current_vars()[name] = Variable(name, type_t, initializer)
            return True
        
    def lookup_variable(self, name:str) -> None | Variable:
        for scope in self.var_table[::-1]:
            if scope.__contains__(name):
                return scope[name]
        return None
    
    def declare_function(self, name:str, type_t:ComplexType, arg_list:list, is_def:bool) -> bool:
        if self.func_table.__contains__(name):
            for func in self.func_table[name]:
                if not func.type_t.can_override(type_t):
                    if func.type_t == type_t and not func.defined and is_def:
                        func.defined = True
                        return True
                    return False
            self.func_table[name].append(Function(name, type_t, arg_list, is_def))
            return True
        else:
            self.func_table[name] = [Function(name, type_t, arg_list, is_def)]
            return True
        
    def lookup_function(self, name:str) -> list[Function]:
        if(self.func_table.__contains__(name)):
            return self.func_table[name]
        else:
            return []
        
    def check(self, node:ASTNode, para:list=None):
        # check root
        if isinstance(node, ASTRoot):
            self.enter_scope()
            for decl in node.decls:
                try:
                    self.check(decl)
                except Exception as ex:
                    print(ex)
                    print("Semantic error detected, compile aborted.")
                    return
            self.leave_scope()

        # check literal
        elif isinstance(node, Literal):
            return (ComplexType(node.type_t), node)
        
        # check identifier ref
        elif isinstance(node, IdentifierRef):
            declared = self.lookup_variable(node.name)
            if declared == None:
                raise NotDeclaredException("Undefined variable: %s" % node.name)
            node.type_t = ComplexType(declared.type_t)
            return (node.type_t, node)
        
        # check unary op
        elif isinstance(node, UnaryOp):
            opd = self.check(node.opd)

            if(isinstance(opd[1], IdentifierRef)):
                var = self.lookup_variable(opd[1].name)
                if(not var.initialized):
                    raise NotInitializedException("%s is not initialized or assigned to any value" % opd[1].name)

            if ComplexType(Types.Double) == opd[0]:
                node.ret_type = ComplexType(Types.Double)
            else:
                node.ret_type = ComplexType(Types.Int)

            return (node.ret_type, node)
        
        # check array index
        elif isinstance(node, ArrayIndex):
            ref = self.lookup_variable(node.base_ref.name)
            node.calc_ret_type(ref.type_t)
            return (node.ret_type, node)
        
        # check binary op
        elif isinstance(node, BinOp):
            l_opd = self.check(node.l_opd)
            r_opd = self.check(node.r_opd)

            if(isinstance(l_opd[1], IdentifierRef)):
                var = self.lookup_variable(l_opd[1].name)
                if(not var.initialized):
                    raise NotInitializedException("%s is not initialized or assigned to any value" % l_opd[1].name)
                
            if(isinstance(r_opd[1], IdentifierRef)):
                var = self.lookup_variable(r_opd[1].name)
                if(not var.initialized):
                    raise NotInitializedException("%s is not initialized or assigned to any value" % r_opd[1].name)

            if ComplexType(Types.Double) == l_opd[0] or ComplexType(Types.Double) == r_opd[0]:
                node.ret_type = ComplexType(Types.Double)
            else:
                node.ret_type = ComplexType(Types.Int)

            return (node.ret_type, node)
        
        # check assign
        elif isinstance(node, Assign):
            l_val = self.check(node.l_val)
            if(isinstance(l_val[1], IdentifierRef)):
                var = self.lookup_variable(l_val[1].name)
                if(var != None):
                    var.initialize()
            self.check(node.r_val)

            if not isinstance(l_val[1], IdentifierRef):
                raise Exception("Cannot assign value to non-reference val %s" % l_val[1])
        
        # check global variable decl
        elif isinstance(node, GlobalVarDecl):
            self.check(node.decl)

        # check function def
        elif isinstance(node, FuncDef):
            success = self.declare_function(node.declarator.identifier.name, node.type_t, node.declarator.arg_list, True)
            if(success):
                self.enter_scope()
                for arg in node.declarator.arg_list:
                    self.declare_variable(arg.identifier.name, arg.type_t, True)
                self.check(node.func_block)
                self.leave_scope()
            else:
                raise DeclDuplicatedException("Duplicated function definition of %s" % node.declarator.identifier.name)
            
        # check decl
        elif isinstance(node, Decl):
            decl_type = node.decl_type
            if decl_type == DeclTypes.Variable:
                success = self.declare_variable(node.declarator.identifier.name, node.type_t, node.declarator.initializer != None)
                if not success:
                    raise DeclDuplicatedException("Duplicated variable declaration of %s" % node.declarator.identifier.name)
                else:
                    self.check(node.declarator)
            elif decl_type == DeclTypes.Function:
                success = self.declare_function(node.declarator.identifier.name, node.type_t, node.declarator.arg_list, False)
                if not success:
                    raise DeclDuplicatedException("Duplicated function declaration of %s" % node.declarator.identifier.name)
                
        # check block stmt
        elif isinstance(node, BlockStmt):
            self.enter_scope()
            for stmt in node.stmt_list:
                self.check(stmt)
            self.leave_scope()

        # check expr stmt
        elif isinstance(node, ExprStmt):
            self.check(node.expr)

        # other symbols
        else:
            return None
            


                    
            
