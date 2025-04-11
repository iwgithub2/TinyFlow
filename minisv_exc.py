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
    def __init__(self):
        self.best_matches = {}
        
    def match_node(self, tree):
        # memoization
        if tree.var in self.best_matches:
            vprint("RETRIEVE", v=DEBUG)
            return self.best_matches[tree.var]
        
        best_cost = math.inf
        best_tree = None
        
        # try to match against all available cells
        for gate_name, (refs,cost) in REF_FORMS.items():
            result = tree.match(refs, gate_name=gate_name)
            vprint("match", tree.var, "with", gate_name, ">>", result, v=DEBUG)
            if result is None:
                continue
            children = []

            for port, wire in result.items():
                node = Node.find_node(wire)
                if node is None:
                    children.append(wire)
                else:
                    vprint("recursing into", node.var, v=DEBUG)
                    m, c = self.match_node(node)
                    cost += c
                    children.append(m)

            if cost < best_cost:
                best_tree = Node(gate_name, children, var=tree.var)
                best_cost = cost

        self.best_matches[tree.var] = best_tree, best_cost
        return best_tree, best_cost