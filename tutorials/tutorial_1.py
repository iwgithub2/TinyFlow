from db.LogicNodes import AND, INV, OR # db.LogicNodes provides built-in logic nodes
from utils.Grapher import dump_node_graph # utils.Grapher provides methods to dump graphs af Nodes

# Create a node with the following structure:
#
#              AND
#             /   \
#           INV   OR
#          /     /  \
#         a     b    c
#
node1 = AND(INV("a"),OR("b","c"))

# dump the pdf and svg for this node to generated/node1.pdf, with label "Tree Visualization"
dump_node_graph(node1, "generated/node1", label="Tree Visualization")