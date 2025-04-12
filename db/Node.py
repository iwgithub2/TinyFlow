from itertools import product
from math import pi
from numbers import Number
from utils.PrettyStream import PrettyStream, vprint, QUIET, INFO, VERBOSE, DEBUG, ALL
from enum import Enum
import json   

class Node():
    """
    A node in an expression tree. Each node represents an instance of a logic gate.
    A node may have two types of children: another node or a leaf. Leafs are strings of input pins.

    Each node maybe be in one of the following states:
    - Pre-synthesis: The original node extracted from SystemVerilog
    - Post-synth: Node containing the technology mapping of the node
    - Post-placement: Node containing the physical placement of the node
    - Post-routing: Node containing the physical routing driven by the node
    """

    class State(Enum):
        PRE_SYNTH = 0
        POST_SYNTH = 1
        POST_PLACE = 2
        POST_ROUTE = 3

    counter = 0
    var_map = {}

    def new_node():
        """
        Get a globally unique identifier for a node's output
        This identifier will be used for mapping the node to its output.
        """
        var =  f"{Node.counter}w"
        Node.counter += 1
        return var
    
    def find_node(var):
        """
        Find a node by its globally unique identifier
        """
        if(var in Node.var_map):
            return Node.var_map[var]
        return None
    
    def __init__(self, children, out=None, db=None):
        self.state = Node.State.PRE_SYNTH
        self.cell_name = None
        self.children = children
        self.input_pins = []
        self.output_pin = None
        self.output_signal = Node.new_node() if out is None else out
        Node.var_map[self.output_signal] = self
        self.output_func = None
        self.optimal_match = None
        self.cuts = []
        self.tree_forms = []

    def in_order_iterator(self):
        for c in self.children:
            if isinstance(c, Node):
                yield from c.in_order_iterator()
            else:
                yield c
        yield self

    def __iter__(self):
        return self.in_order_iterator()

    def get_all_leaf(self):
        input_set = set()
        for i in self:
            if isinstance(i,str):
                input_set.add(i)
        return input_set
    
    def get_all_intermediate(self):
        inter_set = set()
        for i in self:
            if isinstance(i, Node):
                inter_set.add(i.output_signal)
        inter_set.remove(self.output_signal)
        return inter_set
    
    def get_all_input_pattern(self):
        input_set = self.get_all_leaf()
        input_patterns = product([0, 1], repeat=len(input_set))
        input_envs = [dict(zip(list(input_set), bits)) for bits in input_patterns]
        return input_envs

    def pretty(self, p:PrettyStream):
        p << [f'{self.cell_name}|{self.output_signal}']
        with p:
            for c in self.children:
                if isinstance(c, Node):
                    c.pretty(p)
                else:
                    p << c
        return p.cache
    
    def __repr__(self):
        str_children = []
        for c in self.children:
            str_children.append(str(c))
        joined = ",".join(str_children)
        return f"{self.cell_name}|{self.output_signal}({joined})"
    
    def eval_cell(self, *inputs):
        pass
    
    def eval(self, env_dict=None, **env):
        """
        Evaluate the node given an environment
        """
        env = env if env_dict is None else env_dict
        child_env = []
        for child in self.children:
            if isinstance(child, Node):
                child_env.append(child.eval(env))
            elif isinstance(child, Number):
                child_env.append(child)
            elif env[child] is not None:
                child_env.append(env[child])
            else:
                raise ValueError(f"Insufficient env: variable {child} undefined")
        return self.output_func(*child_env)
    
    def logical_eq(self, other):
        """
        Compares two tree for logical equivalence.
        """
        vprint(f"Comparing nodes for logical equivalence", v=DEBUG)
        input_set = self.get_all_leaf()
        other_input_set = other.get_all_leaf()
        if(input_set != other_input_set):
            vprint(f'Leaf mismatch: {input_set} vs {other_input_set}',v=VERBOSE)
            return False
        if(len(input_set) > 7):
            vprint(f'Skipping logical equivalence check with more than 7 inputs', v=INFO)
            return False
        all_patterns = self.get_all_input_pattern()
        vprint(f"Testing {len(all_patterns)} patterns", v=DEBUG)
        for env in all_patterns:
            if(self.eval(env) != other.eval(env)):
                vprint(f"Test Failed with env {env}", v=DEBUG)
                return False
        vprint("The nodes are logically equivalent", v=DEBUG)
        return True
    
    def gate_count(self):
        """
        Counts the gates in the node
        """
        gate_count = {}
        for i in self:
            if isinstance(i, Node):
                if i.cell_name in gate_count:
                    gate_count[i.cell_name] += 1
                else:
                    gate_count[i.cell_name] = 1
        return gate_count    
    
    def to_netlist(self, out=None):
        """
        Converts the node to a netlist
        """
        netlist = []
        conn = {}
        for input, c in zip(self.input_pins, self.children):
            if isinstance(c, Node):
                conn[input] = c.output_signal
            else:
                conn[input] = c

        conn[self.output_pin] = self.output_signal if out is None else out
        netlist.append((self.cell_name,conn))
        for c in self.children:
            if isinstance(c, Node):
                netlist += c.to_netlist()
        return netlist