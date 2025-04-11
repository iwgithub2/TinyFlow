from lark import Lark, Tree, Token
from PrettyStream import *
from TinyDB import TinyDB
from Node import Node
from LogicNodes import *
from copy import deepcopy

def logic_legalize_pass(db: TinyDB):
    """
    Logic legalization pass for the TinyDB
    """
    vprint_title("Logic Legalization Pass", v=INFO)
    db = deepcopy(db)
    for name, tree in db.vars.items():
        vprint(f"Legalizing pin {name}", v=VERBOSE)
        if isinstance(tree, Node):
            tree = legalize_node(deepcopy(tree))
        db.vars[name] = tree
    vprint("Legalized:", db,v=INFO)
    vprint_pretty(db,v=VERBOSE)
    return db

def legalize_node(node: Node):
    """
    Logic legalization pass for a single node
    """
    vprint(f"Legalizing node {node}", v=DEBUG)
    children = [ legalize_node(c) if isinstance(c, Node) else c for c in node.children ]
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
            return NAND(NAND(a, INV(b)), NAND(INV(a), b))
        case _:
            err_msg(f"Unknown node type: {node}")
            raise ValueError(f"Unknown node type: {node}")