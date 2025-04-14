from os import dup
from lark import Lark, Tree, Token
from utils.PrettyStream import *
from db.TinyDB import TinyDB
from db.Node import Node
from db.LogicNodes import *
from copy import deepcopy

def logic_legalize_pass(db: TinyDB, duplicate=True):
    """
    Logic legalization pass for the TinyDB
    """
    vprint_title("Logic Legalization Pass", v=INFO)
    original_db = db
    db = deepcopy(db)
    new_vars={}
    for name, tree in db.vars.items():
        vprint(f"Legalizing pin {name}", v=VERBOSE)
        if isinstance(tree, Node):
            tree = legalize_node(deepcopy(tree),db,new_vars, duplicate=duplicate)
        db.vars[name] = tree
    db.vars |= new_vars
    vprint("Legalized:", db,v=INFO)
    vprint_pretty(db,v=VERBOSE)
    vprint(f"Validating legalized database against original...", v=INFO)
    db.logical_eq(original_db)
    return db

def legalize_node(node: Node, db:TinyDB, new_vars={}, duplicate=True):
    """
    Logic legalization pass for a single node
    """
    vprint(f"Legalizing node {node}", v=DEBUG)
    children = [ legalize_node(c,db,new_vars,duplicate) if isinstance(c, Node) else c for c in node.children ]
    a = children[0]
    b = children[1] if len(children) > 1 else None
    match node:
        case NAND():
            return NAND(a, b)
        case INV():
            return INV(a)
        case AND():
            return INV(NAND(a, b))
        case OR():
            return NAND(INV(a), INV(b))
        case NOR():
            return INV(NAND(INV(a), INV(b)))
        case XOR():
            if not duplicate:
                if isinstance(a,Node):
                    new_vars[a.output_signal]=a
                    a = a.output_signal
                if isinstance(b,Node):
                    new_vars[b.output_signal]=b
                    b = b.output_signal
                return NAND(NAND(a, INV(b)), NAND(INV(a), b))
            else:
                a_copy = a
                if isinstance(a,Node):
                    a_copy = a.copy(True)
                b_copy = b
                if isinstance(b,Node):
                    b_copy = b.copy(True)
                return NAND(NAND(a, INV(b)), NAND(INV(a_copy), b_copy))
        case _:
            err_msg(f"Unknown node type: {node}")
            raise ValueError(f"Unknown node type: {node}")