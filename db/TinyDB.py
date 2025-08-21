from utils.PrettyStream import FAILED, PASSED, PrettyStream, err_msg, vprint, QUIET, INFO, VERBOSE, DEBUG, ALL
from db.Node import *
from db.LogicNodes import *
from db.IOPort import *
from db.Routing import Net

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
        self.vars = {}
        self.ports = {}

        self.node_registry = {}

        self.nets = {}
        self.die_area = None

    def set_die_area(self, half_width, half_height):
        """
        Sets the grid size we are working with for the standard cells
        """
        if half_height < 0 or half_width < 0:
            raise ValueError("Grid size needs to be positive")
        
        self.die_area = (-half_width, -half_height, half_width, half_height)
    
    def get_die_area(self):
        return self.die_area
    
    def _register_node(self, node):
        """
        Register a node in teh node registry
        """
        if isinstance(node, Node):
            self.node_registry[node.node_id] = node
            for child in node.children:
                if isinstance(child, Node):
                    self._register_node(child)
    
    def _unregister_node(self, node):
        """
        Unregister a node and its children from the node registry
        """
        if isinstance(node, Node) and node.node_id in self.node_registry:
            del self.node_registry[node.node_id]
            for child in node.children:
                if isinstance(child, Node):
                    self._unregister_node(child)

    def add_var(self, var_name, expr = None):
        """
        Add a variable to the database
        
        Args:
            var_name (str): The name of the variable
            expr (Node): The expression tree of the variable
        """

        if var_name in self.vars and self.vars.get(var_name) is not None:
            raise ValueError(f"Duplicate definition of variable {var_name} in database {self.name}")
        # Check if we are updating a placeholder (like an output defined before its logic).
        is_update = var_name in self.vars and self.vars[var_name] is None
        # Assign the expression to the variable.
        self.vars[var_name] = expr
        if isinstance(expr, Node):
            self._register_node(expr)
        if is_update:
            vprint(f"Updating variable {var_name} in database", v=VERBOSE)
        
    def add_input(self, var_name, expr = None):
        """
        Add a variable to the database and register is as an input
        """
        if var_name in self.inputs:
            raise ValueError(f"Input {var_name} already exists in module {self.name}")
        self.inputs.add(var_name)
        self.add_var(var_name, expr)

        port = IOPort(var_name, direction=IOPort.Direction.INPUT)
        self.ports[var_name] = port

    def add_output(self, var_name, expr = None):
        """
        Add a variable to the database and register is as an output
        """
        if var_name in self.outputs:
            raise ValueError(f"Output {var_name} already exists in module {self.name}")
        self.outputs.add(var_name)
        self.add_var(var_name, expr)

        port = IOPort(var_name, direction=IOPort.Direction.OUTPUT)
        self.ports[var_name] = port

    def get_node_by_id(self, node_id):
        """
        Get a node by its unique ID.
        
        Args:
            node_id (str): The unique ID of the node
            
        Returns:
            Node: The node object or None if not found
        """
        return self.node_registry.get(node_id)

    def get_all_nodes(self):
        """
        Get all nodes in the database.
        
        Returns:
            dict: Mapping of node_id to Node object
        """
        return self.node_registry.copy()

    def get_placed_nodes(self):
        """
        Get all nodes that have placement information.
        
        Returns:
            dict: Mapping of node_id to Node object for placed nodes
        """
        return {node_id: node for node_id, node in self.node_registry.items() 
                if node.placement}

    def get_unplaced_nodes(self):
        """
        Get all nodes that don't have placement information.
        
        Returns:
            dict: Mapping of node_id to Node object for unplaced nodes
        """
        return {node_id: node for node_id, node in self.node_registry.items() 
                if not node.placement}

    def set_node_placement(self, node_id, x, y, **kwargs):
        """
        Set placement for a node by its ID.
        
        Args:
            node_id (str): The unique ID of the node
            x (float): X coordinate
            y (float): Y coordinate
            **kwargs: Additional placement attributes
            
        Returns:
            bool: True if placement was set successfully, False if node not found
        """
        node = self.get_node_by_id(node_id)
        if node:
            node.set_placement(x, y, **kwargs)
            return True
        return False
    
    def set_port_placement(self, port_name, x, y, **kwargs):
        """
        Set placement for an I/O port by its name.
        """
        if port_name in self.ports:
            self.ports[port_name].set_placement(x, y, **kwargs)
            return True
        return False
    
    def get_inputs(self):
        return self.inputs.copy()
    
    def get_outputs(self):
        return self.outputs.copy()
    
    def add_net(self, net_object):
        """
        Adds a complete Net object to the database.

        Args:
            net_object (Net): An instance of the Net class containing all its
                              wire segments and vias.
        """
        if not isinstance(net_object, Net):
            raise TypeError("Can only add Net objects to the database's netlist.")
        
        if net_object.name in self.nets:
            raise ValueError(f"Net '{net_object.name}' already exists in the database.")
            
        self.nets[net_object.name] = net_object

    def get_net_by_name(self, name):
        """Retrieves a net object by its logical name."""
        return self.nets.get(name)

    def get_all_nets(self):
        """Returns a dictionary of all nets in the database."""
        return self.nets
    
    def get_all_placeable_items(self):
        """
        Get a unified dictionary of all items that need placement.
        This includes all nodes (gates) and all I/O ports.

        Returns:
            dict: A dictionary mapping an item's unique ID (node_id for gates,
                  port_name for ports) to the object itself.
        """
        placeable_items = {}
        # Add all the nodes
        placeable_items.update(self.node_registry)
        # Add all the ports
        placeable_items.update(self.ports)
        return placeable_items

    def make_empty_copy(self):
        new_db = TinyDB(self.name)
        for input in self.inputs:
            new_db.add_input(input)
        for out in self.outputs:
            new_db.add_output(out)
        return new_db

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

    def get_all_input_pattern(self):
        input_set = self.inputs
        input_patterns = product([0, 1], repeat=len(input_set))
        input_envs = [dict(zip(list(input_set), bits)) for bits in input_patterns]
        return input_envs

    def logical_eq(self, other):
        """
        Compares two libraries for logical equivalence.
        """
        vprint("Comparing database equivalence", v=VERBOSE)
        for output in self.outputs:
            if output not in other.outputs:
                vprint(f'Output {output} not found in other database', v=VERBOSE)
                vprint("Databases are not logically equivalent", v=FAILED)
                return False
            tree = self.vars[output]
            if tree is None and other.vars[output] is None:
                continue
            if (tree is None) ^ (other.vars[output] is None):
                vprint(f'Output {output} is not driven in a database', v=VERBOSE)
                vprint("Databases are not logically equivalent", v=FAILED)
            vprint(f"Comparing output {output}",v=VERBOSE)
            if not tree.logical_eq(other.vars[output],self,other):
                vprint("Databases are not logically equivalent", v=FAILED)
                return False
        vprint("Databases are logically equivalent", v=PASSED)
        return True
    
    def eval(self, env_dict=None, db=None,**env):
        """
        Evaluate the database given an environment
        """
        env = env if env_dict is None else env_dict
        result = {}
        for output in self.outputs:
            if output in env:
                err_msg(f"Output {output} conflicts with the environment {env}")
                raise ValueError(env)
            if output not in self.vars or self.vars[output] is None:
                result[output] = "Undriven"
            else:
                result[output] = self.vars[output].eval(env, db)
        return result
                
    def pretty(self, p=PrettyStream()):
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
    
    def get_netlist(self):
        """
        Returns a netlist which is a list of tuples
        Each tuple contains a gate, and its connections
        (gate, dictonary_for_gate, id)
        """
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
            for name, conn, node_id in netlist:
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
        except Exception as e:
            err_msg(f"Failed to write to file {file}", v=FAILED)
            raise e
            
            
            
