#==============================================================================
# Tutorial 1: Building and Visualizing Logic Trees
#==============================================================================

from db.LogicNodes import AND, INV, OR # db.LogicNodes provides built-in logic nodes
import db.Node # db.Node provides the base class for all nodes
from utils.PrettyStream import set_verbose_level, vprint_title, INFO
from utils.Grapher import dump_node_graph # utils.Grapher provides methods to dump graphs af Nodes

set_verbose_level(INFO)

#================================================================================
# Part A
#================================================================================
vprint_title("Part A")

# Create a node with this structure:
#
#              AND
#             /   \
#           INV   OR
#          /     /  \
#         a     b    c
#
# where a, b, and c are inputs
node1 = AND(INV("a"),OR("b","c"))

# Graphs the node and dumps the pdf and svg to generated/tut_1, with label "Tree Visualization"
dump_node_graph(node1, "generated/tut_1/node1", label="Tree Visualization")


# Using the built-in pretty printer to pretty print the node to terminal
print("node1:")
print(node1.pretty())

# You should see the following pretty printed output:
#
# AND|2w
# - INV|0w
#   - a
# - OR|1w
#   - b
#   - c
#
# Notice that each gate is associated with an id such as "0w" or "1w".
# This id represents the output signal of the node, and is globally unique unless explicitly specified
# You may use this id to discern and trace nodes while debugging

#================================================================================
# Part B
#================================================================================
vprint_title("Part B")

# Using the out argument, you can explicitly specify the output signal id:
node2 = AND(INV("a"),OR("b","c",out="or1"),out="and1")
print("node2:")
print(node2.pretty())

# You should see the following pretty printed output:
#
# AND|and1
# - INV|3w
#   - a
# - OR|or1
#   - b
#   - c
#
# Since we didn't specify out for the INV node, it is assigned an id of "3w"