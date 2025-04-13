from db.Node import *
from db.LogicNodes import *
from copy import deepcopy,copy

a = NAND(INV("a"),"b")

# def run():
c = a.copy(new_wire=True)

#     d = c.copy(new_wire=True)

vprint_pretty(a,v=QUIET)
vprint_pretty(c,v=QUIET)
#     vprint_pretty(d,v=QUIET)

# run()