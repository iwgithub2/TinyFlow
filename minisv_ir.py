from enum import Enum
from PrettyStream import PrettyStream
from lark import Tree, Token
from itertools import permutations, product
from PrettyStream import vprint, QUIET, INFO, VERBOSE, DEBUG, ALL
import math

class Module():
    def __init__(self, name):
        self.name = name
        self.vars = {}
        self.inputs = set()
        self.outputs = set()
        self.deps = {}

    def add_var(self, var, expr = None, dep = None):
        if(var in self.vars and self.vars[var] is None):
            self.vars[var] = expr
            self.deps[var] = dep
        elif (not var in self.vars):
            self.vars[var] = expr
            self.deps[var] = dep
        else:
            raise ValueError(f"Duplicate definition of variable {var} in module {self.name}")

    def add_input(self, var, expr = None):
        if var in self.inputs:
            raise ValueError(f"Input {var} already exists in module {self.name}")
        self.inputs.add(var)
        self.add_var(var, expr)

    def add_output(self, var, expr = None):
        if var in self.outputs:
            raise ValueError(f"Output {var} already exists in module {self.name}")
        self.outputs.add(var)
        self.add_var(var, expr)

    def to_json(self):
        return {
            "name": self.name,
            "inports": self.inports,
            "outports": self.outports
        }
    
    def pretty(self):
        p = PrettyStream()
        p << ["module", self.name]
        with p:
            p << ["inputs"]
            with p:
                for i in self.inputs:
                    p << i
            p << ["outputs"]
            with p:
                for o in self.outputs:
                    p << o
            p << ["vars"]
            with p:
                for k, v in self.vars.items():
                    p << [ k, ":", str(v), ]
                    if(k in self.deps and self.deps[k] is not None and len(self.deps[k]) > 0):
                        with p:
                            p << ["dep", ":"] + list(self.deps[k])
        return p.cache

class Node(Tree):
    NO_MATCH = None 
    counter = 0
    
    var_map = {}

    def new_var(ptr):
        var =  f"{Node.counter}w"
        Node.var_map[var] = ptr
        Node.counter += 1
        return var
    
    def find_node(var):
        if(var in Node.var_map):
            return Node.var_map[var]
        return None

    def __init__(self, data, children, cost=0, var=None):
        self.var = var if var is not None else Node.new_var(self)
        super().__init__(data, children)
        self.cost = cost
        self.input_vars = []
        self.terms = 0
        for i in range(len(self.children)):
            c = self.children[i]
            assert isinstance(c,(Node,Token,str))
            if isinstance(c, Node):
                self.input_vars.append(c.var)
                self.cost += c.cost
            elif isinstance(c, Token):
                self.children[i]=c.value
            if isinstance(c, str):
                self.terms += 1
                self.input_vars.append(c)
                n = Node.find_node(c)
                if(n is not None):
                    self.cost += n.cost
        self.is_leaf = self.terms == len(self.children)
        self.optimal_match = None
        self.cuts = []

    def __repr__(self):
        str_children = []
        for c in self.children:
            str_children.append(str(c))
        joined = ",".join(str_children)
        return f"{self.data}|{self.var}({joined})"
    
    def pretty(self):
        return self.pretty_print(PrettyStream()).cache

    def pretty_print(self, p:PrettyStream):
        p << [f'{self.data}|{self.var}']
        with p:
            for c in self.children:
                if isinstance(c, Node):
                    c.pretty_print(p)
                else:
                    p << c
        return p
    
    def match(self, ref, env={}, gate_name = ""):
        # Match with all example forms of a gate
        vprint("   comparing", self.var, "with", gate_name, v=DEBUG)
        for form in ref: 
            if self.data != form.data:
                continue
            if len(self.children) != len(form.children):
                continue
            # try all permutations to match against gate
            for perm in permutations(self.children):
                # Copy of matching environment
                top_env = env.copy() 
                matching_children = 0
                # Match individual Children
                for i in range(len(perm)):
                    c = perm[i] # self's child
                    f = form.children[i] # the form's child

                    # If child is terminal
                    if isinstance(f, str):
                        # break if form's child isn't terminal
                        if not isinstance(c, str):
                            c = c.var
                        # break if form's terminal is already matched to something else
                        if f in top_env and c != top_env[f]:
                            matching_children = -100
                            break
                        # Match this terminal to form's terminal
                        top_env[f] = c
                        matching_children += 1   
                    # If child is node
                    elif isinstance(c, Node):
                        # try to match the node
                        child_env = c.match([f],top_env,f.data)
                        if child_env is None: # break if there is no match
                            break 
                        else: # otherwise update the env
                            top_env.update(child_env)
                            matching_children += 1
                # If all children matched, we found a match
                if matching_children == len(perm):
                    return top_env
        return None

INV     = ("INV",   1)
NAND    = ("NAND",  2)
NOR     = ("NOR",   3)

def m_inv(node):
    return Node(INV[0], [node], INV[1])

def m_nand(node1, node2):
    return Node(NAND[0], [node1, node2], NAND[1])

def m_nor(node1, node2):
    return Node(NOR[0], [node1, node2], NOR[1])

REF_FORMS = {}
REF_FORMS[INV  [0]] = [m_inv("in"),m_nand("in","in")], 1
REF_FORMS[NAND [0]] = [m_nand("a","b")], 2
REF_FORMS[NOR  [0]] = [m_inv(m_nand(m_inv("a"),m_inv("b")))], 3
    
