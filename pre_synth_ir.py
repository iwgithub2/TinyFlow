from lark.tree import Tree
from enum import Enum
from pretty_stream import PrettyStream

class PreSynthIR(Tree):
    
    def __repr__(self):
        p = PrettyStream()
        return self.pretty_print(p).cache
    
    def pretty_print(self, p:PrettyStream):
        return p

class DType(PreSynthIR):
    class BaseType(Enum):
        REG = 1
        WIRE = 2
        INT = 3
        LOGIC = 4

        def __str__(self):
            return self.name.lower()

    def repr_dim(sub_dim):
        repr = ""
        for dim in sub_dim:
            match dim:
                case (start, end):
                    repr += f"[{start}:{end}]"
                case (start,):
                    repr += f"[{start}]"
        return repr

    def __init__(self, base:BaseType, sign = False, dim=([],[])):
        self.base_type = base
        self.sign = sign
        self.dim = dim
    
    def pretty_print(self, p):
        return p.append(DType.repr_dim(self.dim[0]),str(self.base_type),DType.repr_dim(self.dim[1]))
        
    
class Expr(PreSynthIR):
    def __init__(self, data, children, is_constant=False, type:DType=None, dims=([],[])):
        self.data = data
        self.children = children
        self.is_constant = is_constant
        self.type = type
        self.dims = dims

    def __repr__(self):
        return self.data + " " + str(self.children)
    
    def pretty_print(self, p):
        return p << [str(self.data), self.children]
    
class Var(PreSynthIR):
    def __init__(self, name:str, data_type:DType, constant_value=None, expr:Expr=None):
        self.name = name
        self.data_type = data_type
        self.constant_value = constant_value
        self.expr = expr

    def pretty_print(self, p):
        if(self.constant_value is not None):
            return p << [str(self.data_type), "CONST", self.name, "=", self.constant_value]
        return p << ([str(self.data_type), self.name] + (["=", self.expr] if self.expr is not None else []))

class Module(PreSynthIR):
    def __init__(self, name:str, params=[], ports=([],[]), vars=[], procs=[]):
        self.name = name
        self.vars = {}
        print(ports)
        for var in vars:
            self.add_var(var)
        self.ports = (set(),set())
        for port in ports[0]:
            self.add_inport(port)
        for port in ports[1]:
            self.add_outport(port)
        self.params = set()
        for param in params:
            self.add_param(param)
        self.procs = procs
        self.labeled_blocks = {}
        
    def add_var(self, var:Var):
        self.vars[var.name] = var
    
    def add_proc_block(self, proc: Tree):
        self.procs.append(proc)
    
    def add_inport(self, port: Var):
        self.ports[0].add(port.name)
        self.add_var(port)

    def add_outport(self, port: Var):
        self.ports[1].add(port.name)
        self.add_var(port)

    def add_param(self, param: Var):
        self.params.add(param.name)
        self.add_var(param)

    def pretty_print(self, p):
        with p << f"module {self.name}":
            for var in self.vars.values():
                if(var.name in self.ports[0]):
                    p >> "input"
                elif(var.name in self.ports[1]):
                    p >> "output"
                elif(var.name in self.params):
                    p >> "param"
                var.pretty_print(p)
        return p
    
class Instance(PreSynthIR):
    def __init__(self, module_name, name:str, params={}, ports=({},{})):
        self.module = module_name
        self.name = name
        self.params = params
        self.ports = ports

class StaticAssign(PreSynthIR):
    def __init__(self, lhs:Var, rhs:Expr):
        self.lhs = lhs
        self.rhs = rhs
        self.type = None
        self.dims = [],[]

class Sense(PreSynthIR):
    class Edge(Enum):
        POS = 1
        NEG = 2
        NONE = 3
    def __init__(self, edge:Edge, expr:Expr):
        self.edge = edge
        self.expr = expr

class ProcBlock(PreSynthIR):
    class PType(Enum):
        ALWAYS = 1
        ALWAYS_COMB = 2
        ALWAYS_LATCH = 3
        ALWAYS_FF = 4

    def __init__(self, type:PType, senses: list[Sense], block:Tree):
        self.type = type
        self.senses = senses
        self.block = block


