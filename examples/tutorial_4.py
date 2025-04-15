#==============================================================================
# Tutorial 4: Modules and TinyDB
#==============================================================================

from db.TinyDB import TinyDB  # Database representing a macro/module
from db.LogicNodes import AND, INV, OR, XOR
from utils.PrettyStream import vprint_pretty, vprint, set_verbose_level, DEBUG, INFO

set_verbose_level(DEBUG)

# Now that we know all about Logic Trees and Nodes, we can combine them into a design
db = TinyDB("FullAdder") # Create an empty database representing a module

# Pretty print the database
vprint("Printing the empty db:")
vprint_pretty(db,v=DEBUG) 
# We can see that the db is empty at the moment, with no inputs, outputs, or vars(trees)

# To populate the db, we can use the add_input/add_output/add_var methods
db.add_input("a")
db.add_input("b")
db.add_input("cin")

vprint("Printing the db with inputs added:")
vprint_pretty(db,v=DEBUG)

# We can add outputs to the db along with their corresponding logic trees
sum_node = XOR("a",XOR("b","cin"))
db.add_output("sum",sum_node)
vprint("Printing the db with one output added:")
vprint_pretty(db,v=DEBUG)

# We can also add the outputs and deal with the logic trees later
db.add_output("cout")
cout_node = OR(AND("a","b"),OR(AND("b","cin"),AND("a","cin")))
db.vars["cout"] = cout_node

vprint("Printing the db with both outputs added:")
vprint_pretty(db,v=DEBUG)

vprint("Printing the db short hand:")
vprint(str(db),v=DEBUG)

# We can make an empty copy of the db when implementing frontend passes
db_alt = db.make_empty_copy()
# db_alt preserves inputs and outputs, but not the trees
vprint("Printing the empty copy of the db:")

# Suppose we want to instead compute sum in two steps, where:
# sub_sum = a xor b
# sum = sub_sum xor cin

# We can do this by adding a new variable to the db
db_alt.add_var("sub_sum",XOR("a","b"))
vprint("Printing the db with sub_sum added:")
vprint_pretty(db_alt,v=DEBUG)

db_alt.vars["sum"] = XOR("sub_sum","cin")
vprint("Printing the db with sum updated:")
vprint_pretty(db_alt,v=DEBUG)

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

db_alt.vars["cout"] = cout_node.copy(new_wire=True) 

# TinyDB also provides the same logical equivalence check as LogicNodes, it also works on dbs with intermediate variables

# Turn off debug prints to prevent cluttering the output
set_verbose_level(INFO)

vprint("About to compare databases:")
assert(db.logical_eq(db_alt))