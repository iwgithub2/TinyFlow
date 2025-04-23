from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from utils.PrettyStream import *
from passes.ParserPass import parser_pass
from passes.LogicLegalizePass import logic_legalize_pass
from passes.TechMappingPass import tech_mapping_pass
from utils.Grapher import dump_db_graph

from db.LogicNodes import INV, AND, NAND, OR, NOR, XOR, XNOR

#==============================================================================
# Part 1. Building Logic Networks as Trees with TinyFlow
#==============================================================================

# ''' DEMO TASK 1.1 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Build a logic tree for the sum of a full adder
# Inputs: a, b, cin
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
sum_tree = None

# ''' DEMO TASK 1.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Check that the tree is logically correct
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# Helper truth table for sum
sum_tt = [
    [0, 0, 0], 0
    [0, 0, 1], 1
    [0, 1, 0], 1
    [0, 1, 1], 0
    [1, 0, 0], 1
    [1, 0, 1], 0
    [1, 1, 0], 0
    [1, 1, 1], 1
]

# ''' DEMO TASK 1.3 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Pretty print the tree and then dump the graph to a file
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# ''' DEMO TASK 1.4 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Now Build a logic tree for the carry-out of a full adder
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
cout_tree = None

# Helper truth table for cout
cout_tt = [
    [0, 0, 0], 0
    [0, 0, 1], 0
    [0, 1, 0], 0
    [0, 1, 1], 1
    [1, 0, 0], 0
    [1, 0, 1], 1
    [1, 1, 0], 1
    [1, 1, 1], 1
]

#==============================================================================
# Part 2. Building Circuits from Trees with TinyFlow
#==============================================================================

# ''' DEMO TASK 2.1 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Instantiate a TinyDB, and add "a", "b", and "cin" as inputs
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
full_adder = None

# ''' DEMO TASK 2.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Add "cout" and "sum" as outputs, along with their logic trees
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# ''' DEMO TASK 2.3 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Pretty print the TinyDB and then dump the graph to a file
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

#==============================================================================
# Part 3. EDA Frontend with TinyFlow
#==============================================================================

# ''' DEMO TASK 3.1 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Parse the provided Verilog file into a TinyDB
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# ''' DEMO TASK 3.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Convert the TinyDB to NAND-INV form
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# ''' DEMO TASK 3.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Load the TinyLib and Technology map the TinyDB
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# ''' DEMO TASK 3.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Compare the TinyDB from Verilog to the one we built manually
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

set_verbose_level(DEBUG)

db = parser_pass("verilog/FullAdder.sv")
dump_db_graph(db,"generated/test/db_parsed")

db_legal = logic_legalize_pass(db,False)
dump_db_graph(db_legal,"generated/test/db_legal")
assert(db_legal.logical_eq(db))

lib = TinyLib("dbfiles/stdcells.lib")
db_mapped = tech_mapping_pass(db_legal, lib)
db_mapped.dump_verilog("generated/test/FullAdder_mapped.v")
dump_db_graph(db_mapped,"generated/test/db_mapped")
assert(db_legal.logical_eq(db))