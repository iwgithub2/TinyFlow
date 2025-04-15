from db.Node import *
from db.LogicNodes import *
from utils.PrettyStream import *
import json

def NodeFactory(cell_name, pins, forms=[]):
    inputs_pins = []
    output_func = None
    output_pin = None
    tree_forms = []
    for pin_name, pin_value in pins.items():
        if pin_value == 'input':
            inputs_pins.append(pin_name)
    for pin_name, pin_value in pins.items():
        if pin_value != 'input':
            output_pin = pin_name
            output_func = eval(f"lambda {','.join(inputs_pins)}:{pin_value}")
    for form in forms:
        tree_forms.append(eval(form,None,{i:i for i in inputs_pins}))

    def __init__(self, *inputs, out=None):
        super(self.__class__, self).__init__(inputs,out=out)
                
    newclass = type(cell_name, (Node,),{"__init__": __init__, 
                                        "tree_forms": tree_forms, 
                                        "cell_name": cell_name,
                                        "input_pins":inputs_pins,
                                        "output_pin": output_pin,
                                        "output_func": output_func})
    
    vprint(f"Loaded cell {newclass}", v=VERBOSE)

    return newclass

class TinyLib:
    def __init__(self, lib_file="dbfiles/stdcells.lib"):
        vprint_title(f"Loading library", v=INFO)
        self.cells = {}
        self.cell_costs = {}
        self.libname = None
        try:
            with open(lib_file, 'r') as file:
                data = json.load(file)
                self.cells = {}
                self.libname = data["library"]["name"]
                for key, value in data["cells"].items():
                    cell = NodeFactory(key, value["pins"], value["forms"])
                    self.cells[key] = cell
                    self.cell_costs[key] = value["cost"]
                    globals()[key] = cell
                vprint(f"Loaded library {self.libname} with {len(self.cells)} cells", v=INFO)
                vprint(f"Loaded cells: {', '.join(self.cells.keys())}", v=VERBOSE)
        except (KeyError, json.JSONDecodeError) as e:
            err_msg(f"Illegal library file format: {lib_file}")
            raise e
        except FileNotFoundError as e:
            err_msg(f"Library file not found: {lib_file}")
            raise e

    def __repr__(self):
        return f"library {self.libname} ({len(self.cells)} cells)"
    
    def pretty(self, p=None):
        """
        Returns the pretty printed library
        """
        if p is None:
            p = PrettyStream()
        p << ["Library", self.libname]
        with p:
            for k, v in self.cells.items():
                p << v.cell_info()
        return p.cache