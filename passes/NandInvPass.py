from utils.PrettyStream import *
from db.TinyDB import TinyDB
from db.Node import Node
from db.LogicNodes import *

def nand_inv_pass(db: TinyDB, duplicate=False):
    """
    NAND INV conversion pass for the TinyDB
    """
    vprint_title("NAND INV Conversion Pass", v=INFO)
    original_db = db
    # db has inputs and outputs but no insides
    db = original_db.make_empty_copy()
    new_vars={}
    for name, tree in original_db.vars.items():
        vprint(f"Converting pin {name}", v=VERBOSE)
        if isinstance(tree, Node):
            tree = convert_node(tree,new_vars, duplicate=duplicate, out=name)
        db.add_var(name, tree)
    
    for name, tree in new_vars.items():
        db.add_var(name, tree)

    vprint("Converted:", db,v=INFO)
    vprint_pretty(db,v=VERBOSE)
    return db

def convert_node(node: Node, new_vars={}, duplicate=True, out=None):
    """
    NAND INV conversion pass for a single node
    """
    vprint(f"Converting node {node}", v=DEBUG)
    children = [ convert_node(c,new_vars,duplicate,out=c.output_signal) if isinstance(c, Node) else c for c in node.children ]
    a = children[0]
    b = children[1] if len(children) > 1 else None
    match node:
        case NAND():
            return NAND(a, b, out=out)
        case INV():
            return INV(a, out=out)
        case AND():
            return INV(NAND(a, b),out=out)
        case OR():
            return NAND(INV(a), INV(b),out=out)
        case NOR():
            return INV(NAND(INV(a), INV(b)), out=out)
        case XOR():
            if not duplicate:
                if isinstance(a,Node):
                    var_name = a.output_signal+"_var"
                    a.output_signal = var_name
                    new_vars[var_name]=a
                    a = var_name
                if isinstance(b,Node):
                    var_name = b.output_signal+"_var"
                    b.output_signal = var_name
                    new_vars[var_name]=b
                    b = var_name
                return NAND(NAND(a, INV(b)), NAND(INV(a), b), out=out)
            else:
                a_copy = a
                if isinstance(a,Node):
                    a_copy = a.copy(True)
                b_copy = b
                if isinstance(b,Node):
                    b_copy = b.copy(True)
                return NAND(NAND(a, INV(b)), NAND(INV(a_copy), b_copy), out=out)
        case _:
            err_msg(f"Unknown node type: {node}")
            raise ValueError(f"Unknown node type: {node}")