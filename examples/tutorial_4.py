#==============================================================================
# Tutorial 4: TinyDB
#==============================================================================

from db.TinyDB import TinyDB  # Database representing a macro/module
from db.LogicNodes import AND, OR, XOR
from utils.PrettyStream import vprint_pretty, vprint, set_verbose_level, DEBUG, INFO

set_verbose_level(DEBUG)

# Now that we know all about Logic Trees and Nodes, we can combine them into a design
full_adder = TinyDB("FullAdder") # Create an empty database representing a module

# Pretty print the database
vprint("Printing the empty db:")
vprint_pretty(full_adder,v=DEBUG) 
# We can see that the db is empty at the moment, with no inputs, outputs, or vars(trees)

# To populate the db, we can use the add_input/add_output/add_var methods
full_adder.add_input("a")
full_adder.add_input("b")
full_adder.add_input("cin")

vprint("Printing the db with inputs added:")
vprint_pretty(full_adder,v=DEBUG)

# We can add outputs to the db along with their corresponding logic trees
sum_node = XOR("a",XOR("b","cin"))
full_adder.add_output("sum",sum_node)
vprint("Printing the db with one output added:")
vprint_pretty(full_adder,v=DEBUG)

# We can also add the outputs and deal with the logic trees later
full_adder.add_output("cout")
cout_node = OR(AND("a","b"),OR(AND("b","cin"),AND("a","cin")))
full_adder.vars["cout"] = cout_node

vprint("Printing the db with both outputs added:")
vprint_pretty(full_adder,v=DEBUG)

vprint("Printing the db short hand:")
vprint(str(full_adder),v=DEBUG)

# We want to make sure that this database correctly represents a full adder:
all_patterns = full_adder.get_all_input_pattern()
vprint("all_patterns for db:")
vprint(all_patterns, v=DEBUG)

for input in all_patterns:
    outputs = full_adder.eval(input)
    vprint("Outputs for input pattern", input, "are", outputs, v=INFO)

# We can make an empty copy of the db when implementing frontend passes
full_adder_alt = full_adder.make_empty_copy()
# db_alt preserves inputs and outputs, but not the trees
vprint("Printing the empty copy of the db:")

# Suppose we want to instead compute sum in two steps, where:
# sub_sum = a xor b
# sum = sub_sum xor cin

# We can do this by adding a new variable to the db
full_adder_alt.add_var("sub_sum",XOR("a","b"))
vprint("Printing the db with sub_sum added:")
vprint_pretty(full_adder_alt,v=DEBUG)

full_adder_alt.vars["sum"] = XOR("sub_sum","cin")
vprint("Printing the db with sum updated:")
vprint_pretty(full_adder_alt,v=DEBUG)

# we also need to add the tree for cout
# We don't want different database to have same trees, so we can copy the tree for cout_node

# This will create a new tree, but preserving all the node ids
identical_copy = cout_node.copy(new_wire=False)
vprint_pretty("Printing the identical copy of cout_node:")
vprint_pretty(identical_copy,v=DEBUG)

# This will create a new tree, along with new unique ids
new_copy = cout_node.copy(new_wire=True)
vprint_pretty("Printing the new copy of cout_node:")
vprint_pretty(new_copy,v=DEBUG)

full_adder_alt.vars["cout"] = cout_node.copy(new_wire=True) 

# TinyDB also provides the same logical equivalence check as LogicNodes, it also works on dbs with intermediate variables

# Turn off debug prints to prevent cluttering the output
set_verbose_level(INFO)

vprint("About to compare databases:")
assert(full_adder.logical_eq(full_adder_alt))
