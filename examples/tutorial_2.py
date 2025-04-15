#==============================================================================
# Tutorial 2: Evaluating and Comparing Logic Trees
#==============================================================================

from db.LogicNodes import AND, INV, OR, XOR
from utils.PrettyStream import set_verbose_level, ALL

set_verbose_level(ALL)

# This tutorial will show how we can quickly evaluate and compare nodes for testing
node1 = OR(AND(INV("a"),"b"),AND("a",INV("b")))

# Node 1 has the following structure
#
#            OR  
#          /    \
#        AND     AND
#       /  \     /  \
#      INV  b   a  INV
#       |           |
#       a           b 
#

# To evaluate the tree, you can use the provided eval method
print("node1 when a=0 and b=0 outputs:", node1.eval(a=0,b=0))

# Inputs don't have to be a and b, they can be any arbitrary name defined in the tree. 
# For example:
and_node = AND("some_random_var","another_random_var")
print("and_node when some_random_var=1 and another_random_var=0 outputs:", 
      and_node.eval(some_random_var=1,another_random_var=0))

# eval() accept either a list of inputs or a dictionary of inputs 
print("node1 when a=1 and b=0 outputs:", node1.eval({"a":0,"b":1}))

# If not all variables are defined, eval() will fail
try:
    print("\nwe are expecting an error print here:")
    node1.eval(a=0)
except ValueError:
    print("And we caught an exception!")
    pass
# Notice that we receive both an error message from terminal and a ValueError exception

# Now you probably noticed that node1 is actually just an XOR between a and b
# Lets verify this by comparing its outputs to an XOR node:
xor_node = XOR("a","b")
assert node1.eval(a=0,b=0) == xor_node.eval(a=0,b=0)
assert node1.eval(a=0,b=1) == xor_node.eval(a=0,b=1)
assert node1.eval(a=1,b=0) == xor_node.eval(a=1,b=0)
assert node1.eval(a=1,b=1) == xor_node.eval(a=1,b=1)

# This gets very tiring on trees with large number of inputs, so we provide a function for checking this:
# logical_eq() checks for logical equivalence between a pair of trees. 
assert node1.logical_eq(xor_node)

# To be logically equivalent, the trees must 
# - have the same set of inputs/leafs (names must match)
# - generate the same outputs for all possible input combinations 
xor_diff_input = XOR("b","c")
assert not node1.logical_eq(xor_diff_input)
