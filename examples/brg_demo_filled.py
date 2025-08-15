from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from utils.PrettyStream import *
from passes.ParserPass import parser_pass
from passes.NandInvPass import nand_inv_pass
from passes.TechMappingPass import tech_mapping_pass
from utils.Grapher import dump_db_graph, dump_node_graph
from placement.placer import simple_placement

from db.LogicNodes import INV, AND, NAND, OR, NOR, XOR, XNOR

#==============================================================================
# Part 1. Building Logic Networks as Trees with TinyFlow
#==============================================================================

set_verbose_level(DEBUG)

sum_tree = XOR(XOR('a', 'b'), 'cin')

# ''' DEMO TASK 1.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Check that the tree is logically correct
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# Helper truth table for sum
sum_tt = [
    ({'a': 0, 'b': 0, 'cin': 0}, 0),
    ({'a': 0, 'b': 0, 'cin': 1}, 1),
    ({'a': 0, 'b': 1, 'cin': 0}, 1),
    ({'a': 0, 'b': 1, 'cin': 1}, 0),
    ({'a': 1, 'b': 0, 'cin': 0}, 1),
    ({'a': 1, 'b': 0, 'cin': 1}, 0),
    ({'a': 1, 'b': 1, 'cin': 0}, 0),
    ({'a': 1, 'b': 1, 'cin': 1}, 1)
]

for pattern, output in sum_tt:
    assert sum_tree.eval(pattern) == output, f"Sum tree failed for pattern {pattern}"

# ''' DEMO TASK 1.3 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Pretty print the tree and then dump the graph to a file
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

# print(sum_tree.pretty())
dump_node_graph(sum_tree, "generated/brg_demo/sum_tree")

# ''' DEMO TASK 1.4 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Now Build a logic tree for the carry-out of a full adder
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
cout_tree = OR(AND('a', 'b'), AND('cin', XOR('a', 'b')))
dump_node_graph(cout_tree, "generated/brg_demo/cout_tree")

# Helper truth table for cout
cout_tt = [
    ({'a': 0, 'b': 0, 'cin': 0}, 0),
    ({'a': 0, 'b': 0, 'cin': 1}, 0),
    ({'a': 0, 'b': 1, 'cin': 0}, 0),
    ({'a': 0, 'b': 1, 'cin': 1}, 1),
    ({'a': 1, 'b': 0, 'cin': 0}, 0),
    ({'a': 1, 'b': 0, 'cin': 1}, 1),
    ({'a': 1, 'b': 1, 'cin': 0}, 1),
    ({'a': 1, 'b': 1, 'cin': 1}, 1)
]

for pattern, output in cout_tt:
    assert cout_tree.eval(pattern) == output, f"Cout tree failed for pattern {pattern}"

#==============================================================================
# Part 2. Building Circuits from Trees with TinyFlow
#==============================================================================

# ''' DEMO TASK 2.1 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Instantiate a TinyDB, and add "a", "b", and "cin" as inputs
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
full_adder = TinyDB("FullAdder")
full_adder.add_input('a')
full_adder.add_input('b')
full_adder.add_input('cin')

# ''' DEMO TASK 2.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Add "cout" and "sum" as outputs, along with their logic trees
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
full_adder.add_output('cout', cout_tree)
full_adder.add_output('sum', sum_tree)

# ''' DEMO TASK 2.3 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Pretty print the TinyDB and then dump the graph to a file
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
# print(full_adder.pretty())
dump_db_graph(full_adder, "generated/brg_demo/full_adder")

#==============================================================================
# Part 3. EDA Frontend with TinyFlow
#==============================================================================

# ''' DEMO TASK 3.1 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Parse the provided Verilog file into a TinyDB
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
db = parser_pass("verilog/FullAdder.sv")
dump_db_graph(db,"generated/brg_demo/db_parsed")

# ''' DEMO TASK 3.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Convert the TinyDB to NAND-INV form
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
db_nandinv = nand_inv_pass(db,False)
dump_db_graph(db_nandinv,"generated/test/db_nand_inv")
assert(db_nandinv.logical_eq(db))

# ''' DEMO TASK 3.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Load the TinyLib and Technology map the TinyDB
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
lib = TinyLib("dbfiles/stdcells.lib")
db_mapped = tech_mapping_pass(db_nandinv, lib)
db_mapped.dump_verilog("generated/test/FullAdder_mapped.v")
dump_db_graph(db_mapped,"generated/test/db_mapped")
assert(db_nandinv.logical_eq(db))

# ''' DEMO TASK 3.2 '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Compare the TinyDB from Verilog to the one we built manually
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
assert(db_mapped.logical_eq(full_adder))

# Call the placer using the technology mapped version of the netlist
simple_placement(db_mapped, lib)