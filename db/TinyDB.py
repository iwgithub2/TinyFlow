from itertools import permutations, product
from math import e, pi
from utils.PrettyStream import FAILED, PASSED, PrettyStream, err_msg, vprint, QUIET, INFO, VERBOSE, DEBUG, ALL
from enum import Enum
import json
from db.Node import *
from db.LogicNodes import *

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
        vprint("Comparing database equivalence", v=VERBOSE)
        for output in self.outputs:
            if output not in other.outputs:
                vprint("Databases are not logically equivalent", v=FAILED)
                return False
            tree = self.vars[output]
            if tree is None and other.vars[output] is None:
                continue
            vprint(f"Comparing output {output}",v=VERBOSE)
            if not tree.logical_eq(other.vars[output],self,other):
                vprint("Databases are not logically equivalent", v=FAILED)
                return False
        vprint("Databases are logically equivalent", v=PASSED)
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
                    # p << [ k, ":" ]
                    # if isinstance(v, Node):
                    #     v.pretty(p)
                    # elif isinstance(v, str):
                    #     p << [v]
                    # else:
                    #     p << [str(v)]
                    p << [ f'{k}:', str(v), ]
        return p.cache

    def __repr__(self):
        return f"{self.name}({','.join(self.inputs)})->{','.join(self.outputs)}"
    
    def get_netlist(self):
        netlist = []
        for v, n in self.vars.items():
            if isinstance(n, Node):
                netlist.extend(n.to_netlist(out=v))
        return netlist
    
    def gate_count(self):
        gate_count = {}
        for v, n in self.vars.items():
            if isinstance(n, Node):
                node_gate_count = n.gate_count()
                for k, v in node_gate_count.items():
                    if k in gate_count:
                        gate_count[k] += v
                    else:
                        gate_count[k] = v
        return gate_count        

    def dump_verilog(self, file):
        """
        Dump the database to a verilog file
        """
        vprint(f"Dumping verilog to {file}", v=INFO)
        gate_count = self.gate_count()
        gate_count_str = ''.join([ '\n- ' + k + ': ' + str(v) for k, v in gate_count.items() ])
        vprint(f"{self.name} gate count: {gate_count_str}", v=VERBOSE)

        p = PrettyStream(trail_sep='  ')
        p << "// Generated by TinyFlow"
        p << ["module", self.name+"("]
        with p:
            for i in self.inputs:
                p << ["input  logic", f'{i},']
            outputs = list(self.outputs)
            for o in outputs[:-1]:
                p << ["output logic",f'{o},']
            p << ["output logic", outputs[-1]]
        p << ");"
        ports = set(self.inputs) | set(self.outputs)
        locals = list(set(self.vars.keys()) - ports)
        netlist = self.get_netlist()
        inter = set()
        for v, c in self.vars.items():
            if isinstance(c, Node):
                inter |= c.get_all_intermediate()
    
        with p:
            p << ["// Local variables"]
            for l in locals:
                p << ["logic", f'{l};']
            p << ["// Generated nets"]
            for i in inter:
                p << ["logic", f'{i};']
            p << ["// Generated gates"]
            id = 0
            for name, conn in netlist:
                p << [name, 'g'+str(id), "("]
                id += 1
                with p:
                    conn = list(conn.items())
                    for pin, wire in conn[:-1]:
                        p << f'.{pin}({wire}),'
                    p << f'.{conn[-1][0]}({conn[-1][1]})'
                p << [");"]
        p << ["endmodule"]

        try: 
            with open(file, 'w') as f:
                f.write(p.cache)
                f.write('\n')
                f.close()
                vprint(f"Dumped verilog to {file}", v=INFO)
        except e:
            err_msg(f"Failed to write to file {file}", v=FAILED)
            raise e
            
            
            
