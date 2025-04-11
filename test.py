from TinyDB import TinyDB, load_tiny_lib
from PrettyStream import set_verbose_level, DEBUG, err_msg, vprint, vprint_pretty
from LogicNodes import NAND, INV, AND
from ParserPass import parser_pass
from LogicLegalizePass import logic_legalize_pass

set_verbose_level(DEBUG)
load_tiny_lib("dbfiles/stdcells.lib")
db = TinyDB("test")

# a = NAND2D1("a","a")
# b = INVD1("b")

# a_log = NAND("a","a")
# b_log = INV("b")

# print(a.logical_eq(a_log))
# print(b.logical_eq(b_log))

# vprint("HELLO WORKD", v=INFO)
# err_msg("TEST")

# print(a.logical_eq(b))

db = parser_pass("FullAdder.sv")
db_legal = logic_legalize_pass(db)

assert(db.logical_eq(db_legal))

expr = db.vars["sum"]
and3 = AND("a",AND("b",1))

# print(a)
# a.pretty_print()
# print(a.eval_cell(1,1))
# print(a.eval(a=0,b=1))

# and_func = "c[0] & c[1]"

# c = eval(f"lambda c:{and_func}")

# print(c([1,2]))