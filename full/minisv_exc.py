from minisv_ir import *
from lark.visitors import Visitor, Transformer, v_args
from lark.tree import Tree
from lark.lexer import Token
from PrettyStream import vprint, PrettyStream
import math

class IRExtractionPass(Visitor):
    def __init__(self):
        self.modules = {}
        self.visit_cache = None

    def visit_return(self, tree):
        self.visit_topdown(tree)
        return self.visit_cache
        
    def decl(self, tree):
        self.visit_cache = tree.children[0].value

    def assignment(self, tree):
        var = tree.children[0].value
        expr = tree.children[1]
        self.visit_cache = set()
        deps = self.visit_return(expr)
        self.visit_cache = (var, expr, deps)

    def expr(self, tree):
        for child in tree.children:
            match child:
                case Token(type="ID", value=name):
                    if(isinstance(self.visit_cache, set)):
                        self.visit_cache.add(name)
                    
    def port_decl_list(self, tree):
        ports = ([],[])
        for port_decl in tree.children:
            if(port_decl.children[0].value == "input"):
                ports[0].append(port_decl.children[1].value)
            elif(port_decl.children[0].value == "output"):
                ports[1].append(port_decl.children[1].value)
        self.visit_cache = ports
    
    def module(self, tree):
        module = Module(tree.children[0].value)
        for child in tree.children:
            match child:
                case Tree(data="port_decl_list"):
                    ports = self.visit_return(child)
                    for port in ports[0]:
                        module.add_input(port)
                    for port in ports[1]:
                        module.add_output(port)
                case Tree(data="decl"):
                    module.add_var(self.visit_return(child))
                case Tree(data="assignment"):
                    module.add_var(*self.visit_return(child))
        self.modules[module.name] = module


class VarSubTransform(Transformer):
    def __init__(self, module):
        self.module = module
    
    @v_args(tree=True)
    def expr(self, tree):
        new_children = []
        for children in tree.children:
            match children:
                case Token(type="ID", value=name):
                        if(not name in self.module.inputs):
                            new_children.append(self.module.vars[name])
                        else:
                            new_children.append(children)
                case _:
                    new_children.append(children)
        return Tree(data = tree.data, children = new_children)

class ForestryPass():
    def __init__(self, module):
        self.module = module
        self.visited = set()

    def execute(self):
        for var in self.module.vars:
            self.visit_var(var)
            vprint(f"Afforested {var}",v=VERBOSE)
            vprint(f"  -> {self.module.vars[var]}",v=VERBOSE)
    
    def visit_var(self, var):
        if var in self.visited:
            return
        if self.module.deps[var] is None or len(self.module.deps[var]) == 0:
            return
        
        for dep in self.module.deps[var]:
            self.visit_var(dep)
        
        self.module.vars[var] = VarSubTransform(self.module).transform(self.module.vars[var])
        print(f"  -> {self.module.vars[var]}")

        self.visited.add(var)
        
class LogicPass(Transformer):

    @v_args(tree=True)
    def bit_or(self, tree):
        return m_inv(m_nor(tree.children[0], tree.children[1]))
    
    @v_args(tree=True)
    def bit_and(self, tree):
        return m_inv(m_nand(tree.children[0], tree.children[1]))

    @v_args(tree=True)
    def bit_nand(self,tree):
        return m_nand(tree.children[0], tree.children[1])
    
    @v_args(tree=True)
    def bit_nor(self,tree):
        return m_nor(tree.children[0], tree.children[1])
    
    
    @v_args(tree=True)
    def bit_not(self, tree):
        return m_inv(tree.children[0])
    
    @v_args(tree=True)
    def bit_xor(self, tree):
        x = m_nand(tree.children[0], tree.children[1])
        y = m_nand(tree.children[0], x)
        z = m_nand(tree.children[1], x)
        res = m_nand(y, z)
        vprint("MAKE XOR:",res.pretty(), v=ALL)
        return res
    
    @v_args(tree=True)
    def bit_xnor(self, tree):
        x = m_nand(tree.children[0], tree.children[1])
        y = m_nand(tree.children[0], x)
        z = m_nand(tree.children[1], x)
        return m_inv(m_nand(y, z))

class TreeCoveringPass():
    def __init__(self, gates):
        self.gates = gates
        self.best_matches = {}
        
    def match_node(self, tree, vv=False):
        if tree in self.best_matches:
            vprint("RETRIEVE", v=DEBUG)
            return self.best_matches[tree]

        tts = tree.enum_tts()
        best_cost = math.inf
        best_match = None
        for tree_tt in tts:
            for (name, gt, num_ins, gcost) in self.gates:
                if(tree_tt.canon[0] == 0b0110):
                    vprint("MAYBE XOR:", tree_tt,v=ALL)
                if(gt == tree_tt.canon[0] and num_ins == len(tree_tt.ins)):
                    #print(f"Checking {name} against {tree_tt}")
                    canon_tree_tt = tree_tt.canonicalize()
                    children = []
                    for inp in canon_tree_tt.ins:
                        n = Node.find_var(inp)
                        if( n is None):
                            children.append(inp)
                        else:
                            children.append(self.match_node(n))
                    match = Node(name, children, gt, gcost, tree.var)
                    # vprint("Found match:", match, v=VERBOSE)
                    if( match.cost < best_cost):
                        best_cost = match.cost
                        best_match = match

        self.best_matches[tree] = best_match
        return best_match
                    
                            

                            