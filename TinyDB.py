from itertools import permutations, product
from math import pi
from PrettyStream import PrettyStream, vprint, QUIET, INFO, VERBOSE, DEBUG, ALL
from enum import Enum
import json
from Node import *

def load_tiny_lib(lib_file="dbfiles/stdcells.lib"):
    if lib_file is not None:
        with open(lib_file, 'r') as file:
            data = json.load(file)
            for key, value in data["cells"].items():
                globals()[key] = NodeFactory(key, value["pins"])

class TinyDB:
    """
    The core database for TinyFlow. Each database represents a module/macro.
    The database holds all data of the module through different stages of synthesis.
    """
    def __init__(self, name):
        """
        Initialize a new database.
        """
        self.name = name
        self.inputs = set()
        self.outputs = set()
        self.cells = {}
        self.vars = {}

    def add_var(self, var_name, expr = None):
        """
        Add a variable to the database
        
        Args:
            var_name (str): The name of the variable
            expr (str): The expression tree of the variable
        """

        if(var_name in self.vars and self.vars[var_name] is None):
            self.vars[var_name] = expr
            vprint(f"Updating variable {var_name} in database", v=VERBOSE)
        elif (not var_name in self.vars):
            self.vars[var_name] = expr
        else:
            raise ValueError(f"Duplicate definition of variable {var_name} in database {self.name}")
        
    def add_input(self, var_name, expr = None):
        """
        Add a variable to the database and register is as an input
        """
        if var_name in self.inputs:
            raise ValueError(f"Input {var_name} already exists in module {self.name}")
        self.inputs.add(var_name)
        self.add_var(var_name, expr)

    def add_output(self, var_name, expr = None):
        """
        Add a variable to the database and register is as an output
        """
        if var_name in self.outputs:
            raise ValueError(f"Output {var_name} already exists in module {self.name}")
        self.outputs.add(var_name)
        self.add_var(var_name, expr)

    def to_json(self):
        """
        Serialize the database to a JSON object for debugging
        """
        return {
            "name": self.name,
        }
    
    def from_json(self, json):
        """
        Deserialize the database from a JSON object for debugging
        """
        self.name = json["name"]

    def export_verilog(self,file):
        pass

    def logical_eq(self, other):
        """
        Compares two libraries for logical equivalence.
        """
        for pin, tree in self.vars.items():
            if pin not in other.vars:
                return False
            if tree is None and other.vars[pin] is None:
                continue
            if not tree.logical_eq(other.vars[pin]):
                return False
        return True

    def pretty(self, p:PrettyStream):
        """
        Returns the pretty printed database
        """
        p << ["TinyDB", self.name]
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
                    p << [ f'{k}:', str(v), ]
        return p.cache

    def __repr__(self):
        return f"{self.name}({','.join(self.inputs)})->{','.join(self.outputs)}"