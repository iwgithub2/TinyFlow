from lark import Lark, Tree, Token
from utils.PrettyStream import *
from db.TinyDB import TinyDB
from db.Node import Node
from db.LogicNodes import *

def parser_pass(input_file):
    """
    Parse the input file and return the database
    """
    vprint_title("Parser Pass")
    ast = parse(input_file)
    db = extract_db(ast)
    vprint("Parsed:", db,v=INFO)
    vprint_pretty(db,v=VERBOSE)
    return db

def parse(filename, grammar="grammars/minisv.lark"):
    with open(filename) as f:
        text = f.read()
    with open(grammar) as f:
        grammar = f.read()
    parser = Lark(grammar, start="start", parser="lalr")
    return parser.parse(text)

def extract_db(ast_tree):
    db = TinyDB("stub")
    visit(ast_tree, db)
    return db

def visit(ast_node, db):
    if isinstance(ast_node, Tree):
        match ast_node.data:
            case "module":
                db.name = ast_node.children[0]
                for c in ast_node.children:
                    visit(c,db)
            case "port_decl_list":
                for c in ast_node.children:
                    visit(c, db)
            case "port_decl":
                
                match ast_node.children:
                    case [Token("DIR","input"), Token("ID",id)]:
                        db.add_input(id)
                        vprint(f"Input port: {id}", v=VERBOSE)
                    case [Token("DIR","output"), Token("ID",id)]:  
                        db.add_output(id)
                        vprint(f"Output port: {id}", v=VERBOSE)
            case "assignment":
                match ast_node.children:
                    case [Token("ID",id), expr]:
                        db.add_var(id, visit_expr(expr,out=id))
            case "decl":
                db.add_var(ast_node.children[0].value)
            case _:
                err_msg(f"Unknown AST node type: {ast_node.data}")
                vprint(ast_node, v=DEBUG)
    return

def visit_expr(ast_node, out=None):
    if isinstance(ast_node, Tree):
        match ast_node.data:
            case "bit_or":
                return OR(visit_expr(ast_node.children[0]), visit_expr(ast_node.children[1]),out=out)
            case "bit_and":
                return AND(visit_expr(ast_node.children[0]), visit_expr(ast_node.children[1]),out=out)
            case "bit_nand":
                return NAND(visit_expr(ast_node.children[0]), visit_expr(ast_node.children[1]),out=out)
            case "bit_nor":
                return NOR(visit_expr(ast_node.children[0]), visit_expr(ast_node.children[1]),out=out)
            case "bit_xnor":
                return XNOR(visit_expr(ast_node.children[0]), visit_expr(ast_node.children[1]),out=out)
            case "bit_xor":
                return XOR(visit_expr(ast_node.children[0]), visit_expr(ast_node.children[1]),out=out)
            case "bit_not":
                return INV(visit_expr(ast_node.children[0]),out=out)
            case _:
                err_msg(f"Unknown expression type: {ast_node.data}")
    elif isinstance(ast_node, Token):
        match ast_node.type:
            case "ID":
                return ast_node.value
            case "LITERAL":
                match ast_node.value:
                    case "0" | "1'b0":
                        return 0
                    case "1" | "1'b1":
                        return 1
                    case _:
                        err_msg(f"Unknown literal value: {ast_node.value}")
                return ast_node.value
            case _:
                err_msg(f"Unknown token type: {ast_node.type}")
    return ast_node