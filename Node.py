from itertools import product
from math import pi
from numbers import Number
from PrettyStream import PrettyStream, vprint, QUIET, INFO, VERBOSE, DEBUG, ALL
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

    def new_node(node):
        """
        Get a globally unique identifier for a node's output
        This identifier will be used for mapping the node to its output.
        """
        var =  f"{Node.counter}w"
        Node.var_map[var] = node
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
        self.output_signal = Node.new_node(self) if out is None else out
        self.output_func = None
        self.optimal_match = None
        self.cuts = []

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
        input_set = self.get_all_leaf()
        other_input_set = other.get_all_leaf()
        if(input_set != other_input_set):
            vprint(f'Leaf mismatch: {input_set} vs {other_input_set}',v=VERBOSE)
            return False
        if(len(input_set) > 7):
            vprint(f'Skipping logical equivalence with more than 7 inputs', v=INFO)
            return False
        for env in self.get_all_input_pattern():
            if(self.eval(env) != other.eval(env)):
                vprint(f"Test Failed with env {env}", v=DEBUG)
                return False
        return True

def NodeFactory(cell_name, pins):
    inputs = []
    output_func = None
    output_pin = None
    for pin_name, pin_value in pins.items():
        if pin_value == 'input':
            inputs.append(pin_name)
    for pin_name, pin_value in pins.items():
        if pin_value != 'input':
            output_pin = pin_name
            output_func = eval(f"lambda {','.join(inputs)}:{pin_value}")

    def __init__(self, *inputs, out=None):
        super(self.__class__, self).__init__(inputs,out=out)
        self.cell_name = cell_name
        self.input_pins = inputs
        self.output_func = output_func
        self.output_pin = output_pin

        def eval_cell(*inputs):
            return self.output_func(*inputs)
        
        self.eval_cell = eval_cell
                
    newclass = type(cell_name, (Node,),{"__init__": __init__})
    return newclass
