from itertools import product
from numbers import Number
from utils.PrettyStream import *
from enum import Enum
from copy import copy
import uuid

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

    cell_name = None
    input_pins = []
    output_func = lambda *_ : False
    output_pin = None
    patterns = []

    def new_node():
        """
        Get an identifier for the node for debugging.
        """
        var =  f"{Node.counter}w"
        Node.counter += 1
        return var
    
    @classmethod
    def cell_info(cls):
        return f"{cls.cell_name}({','.join(cls.input_pins)})->{cls.output_pin} [{len(cls.patterns)} patterns]"
    
    def __init__(self, children, out=None):
        self.state = Node.State.PRE_SYNTH
        self.children = children
        for c in children:
            if c == 'db' or c == 'env_dict' or c == 'env':
                err_msg(f"{c} is a reserved keyword and cannot be used as an input")
                raise ValueError(c)
        self.output_signal = Node.new_node() if out is None else out
        self.optimal_match = None
        self.cuts = []

        self.node_id = str(uuid.uuid4())
        self.placement = None
        self.placement_attributes = {}
    
    def set_placement(self, x, y):
        self.placement = (x, y)
        if self.state.value < Node.State.POST_PLACE.value:
            self.state = Node.State.POST_PLACE
    
    def get_placement(self):
        return self.placement
    
    def is_placed(self):
        return self.placement is not None

    def get_all_nodes_with_ids(self):
        nodes = {}
        for node in self:
            if isinstance(node, Node):
                nodes[node.node_id] = node
        return nodes

    def in_order_iterator(self):
        for c in self.children:
            if isinstance(c, Node):
                yield from c.in_order_iterator()
            else:
                yield c
        yield self

    def __iter__(self):
        return self.in_order_iterator()

    def get_all_leaf(self, db=None):
        input_set = set()
        for i in self:
            if isinstance(i,str):
                if db is not None and i in db.vars and isinstance(db.vars[i],Node):
                    input_set |= db.vars[i].get_all_leaf(db)
                else:
                    input_set.add(i)
        return input_set
    
    def get_all_intermediate(self):
        inter_set = set()
        for i in self:
            if isinstance(i, Node):
                inter_set.add(i.output_signal)
        inter_set.remove(self.output_signal)
        return inter_set
    
    def copy(self, new_wire=True):
        new_children = [c.copy(new_wire) if isinstance(c, Node) else c for c in self.children]
        new_node = self.__class__(*new_children)
        if new_wire:
            new_node.output_signal = Node.new_node()
        else:
            new_node.output_signal = self.output_signal
        return new_node
    
    def get_all_input_pattern(self,db=None):
        input_set = self.get_all_leaf(db)
        input_patterns = product([0, 1], repeat=len(input_set))
        input_envs = [dict(zip(list(input_set), bits)) for bits in input_patterns]
        return input_envs

    def pretty(self, p=None):
        if p is None:
            p = PrettyStream()
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
    
    def eval(self, env_dict=None, db=None,**env):
        """
        Evaluate the node given an environment
        """
        env = env if env_dict is None else env_dict
        child_env = []
        for child in self.children:
            if isinstance(child, Node):
                if child.output_signal in env:
                    child_env.append(env[child])
                else:
                    child_env.append(child.eval(env,db))
            elif isinstance(child, Number):
                child_env.append(child)
            elif child in env:
                child_env.append(env[child])
            elif db is not None and child in db.vars and isinstance(db.vars[child],Node):
                child_env.append(db.vars[child].eval(env,db))
            else:
                err_msg(f"Insufficient env: variable {child} undefined")
                raise ValueError(child)
        return type(self).output_func(*child_env)
    
    def logical_eq(self, other, my_db=None, other_db=None):
        """
        Compares two tree for logical equivalence.
        """
        vprint(f"Comparing\n{self.pretty(PrettyStream())}\nwith\n{other.pretty(PrettyStream())}for logical equivalence", v=DEBUG)
        input_set = self.get_all_leaf(my_db)
        other_input_set = other.get_all_leaf(other_db)
        if(input_set != other_input_set):
            vprint(f'Leaf mismatch: {input_set} vs {other_input_set}',v=FAILED)
            return False
        if(len(input_set) > 7):
            err_msg(f'Skipping logical equivalence check with more than 7 inputs')
            return False
        all_patterns = self.get_all_input_pattern(my_db)
        vprint(f"Testing {len(all_patterns)} patterns", v=DEBUG)
        for env in all_patterns:
            se = self.eval(env,my_db)
            oe = other.eval(env,other_db)
            vprint(f'Tested Pattern {env}, {int(se)}|{int(oe)}',v=DEBUG)
            if(self.eval(env,my_db) != other.eval(env,other_db)):
                vprint(f"Test Failed", v=FAILED)
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
        Returns a tuple (gate, connections, id)
        """
        netlist = []
        conn = {}
        for input, c in zip(self.input_pins, self.children):
            if isinstance(c, Node):
                conn[input] = c.output_signal
            else:
                conn[input] = c

        conn[self.output_pin] = self.output_signal if out is None else out
        netlist.append((self.cell_name,conn, self.node_id))
        for c in self.children:
            if isinstance(c, Node):
                netlist += c.to_netlist()
        return netlist