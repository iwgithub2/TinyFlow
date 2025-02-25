from lark.visitors import Transformer, Visitor, v_args
from lark.tree import Tree
from lark.lexer import Token
from enum import Enum
from pre_synth_ir import *

class ExprSubstitutePass(Transformer):
    def __init__(self):
        self.variables = {}
        self.constants = {}
        self.exprs = {}

    @v_args(tree=True)
    def expr(self, tree):
        return Expr(tree.data, tree.children)

class IRExtractionPass(Visitor):
    def __init__(self):
        self.modules = {}
        self.visit_cache = None

    def visit_return(self, tree):
        self.visit(tree)
        return self.visit_cache

    def DTYPE(self, token):
        parts = token.value.split()
        base = DType.BaseType.INT
        sign = True
        if "reg" in parts:
            base = DType.BaseType.REG
            sign = False
        elif "wire" in parts:
            base = DType.BaseType.WIRE
            sign = False
        elif "logic" in parts:
            base = DType.BaseType.LOGIC
            sign = False
        
        if "signed" in parts:
            sign = True
        elif "unsigned" in parts:
            sign = False
        return DType(base, sign)

    def decl_typed(self, tree):
        self.opt_decl(tree)

    def decl_def(self, tree):
        self.opt_decl(tree)

    def decl(self, tree):
        self.opt_decl(tree)
    
    def opt_decl(self, tree):
        dtype = DType(DType.BaseType.INT)
        dim_list = ([], [])
        packed = True
        expr = None
        name = None
        for child in tree.children:
            match child:
                case Token(type="DTYPE"):
                    dtype = self.DTYPE(child)
                case Tree(data="dim", children=[start, end]):
                    dim_list[0 if packed else 1].append((start, end))
                case Tree(data="dim", children=[start]):
                    dim_list[0 if packed else 1].append((start,))
                case Token(type="ID"):
                    name = child.value
                    packed = False
                case Tree(data="expr"):
                    expr = child
        dtype.dim = dim_list
        self.visit_cache = Var(name, dtype, expr=expr)

    def param_decl_list(self, tree):
        params = []
        for port_decl in tree.children:
            var = self.visit_return(port_decl)
            params.append(var)
        self.visit_cache = params
    
    def port_decl_list(self, tree):
        ports = ([],[])
        for port_decl in tree.children:
            var = self.visit_return(port_decl)
            if(port_decl.children[0].value == "input"):
                ports[0].append(var)
            elif(port_decl.children[0].value == "output"):
                ports[1].append(var)
        self.visit_cache = ports
    
    def module(self, tree):
        procs = []
        params = []
        ports = ({}, {})
        procs = []
        vars = {}
        for child in tree.children:
            match child:
                case Token(type="ID"):
                    module_name = child.value
                case Tree(data="param_decl_list"):
                    params = self.visit_return(child)
                case Tree(data="port_decl_list"):
                    ports = self.visit_return(child)
        self.modules[module_name] = Module(module_name, params, ports, vars, procs)

class ConstantFolder(Transformer):
    def __init__(self):
        self.constants = {}

    def constant(self, value):
        return value
    
    def add(self, a, b):
        if isinstance(a, int) and isinstance(b, int):
            return a + b
        return a + b
