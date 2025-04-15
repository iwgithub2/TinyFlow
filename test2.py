from db.LogicNodes import AND, INV, OR
from utils.Grapher import dump_node_graph

node1 = AND(INV("a"),OR("b","c"))

dump_node_graph(node1, "generated/node1", "Tree Visualization")