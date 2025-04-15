from encodings.idna import dots
from graphviz import Digraph
from db.Node import Node
from db.TinyDB import TinyDB

def graph_node(node:Node, dot=None, label=None, prefix="", graphed=set()):
    if node in graphed:
        return dot
    
    graphed.add(node)

    if dot is None:
        dot = Digraph(comment="Tree Visualization")

    if label is not None:
        dot.attr(label=label, labelloc="tl", fontsize="15")

    # Add the current node
    dot.node(node.output_signal, node.cell_name)

    # Recursively add all children nodes and connect them via edges.
    for child in node.children:
        if isinstance(child,Node):
            dot.node(child.output_signal, child.cell_name)  # Ensure the child exists in the graph.
            graph_node(child, dot, prefix=prefix,graphed=graphed)
            dot.edge(node.output_signal, child.output_signal, child.output_signal, fontsize="10")
        else:
            dot.node(prefix+child, child, color="black", fillcolor="darkolivegreen1", style="filled",shape="box")
            dot.edge(node.output_signal, prefix+child)
    return dot

def graph_db(db:TinyDB):
    cluster = Digraph(name=db.name)
    cluster.attr(label=db.name, labelloc="tl", fontsize="15")
    for pin, node in db.vars.items():
        if isinstance(node,Node):
            c = "darkslategray1" if pin in db.outputs else "khaki1"
            cluster.node("pin"+pin,pin,color="black", fillcolor=c, style="filled",shape="box")
            cluster.edge("pin"+pin,node.output_signal,node.output_signal,fontsize="10")
            graph_node(node, cluster,prefix=pin)
    return cluster

def dump_db_graph(db:TinyDB, filename):
    dot = graph_db(db)
    dot.render(filename, view=False)
    dot.format = 'svg'
    dot.render(filename, view=False)

def dump_node_graph(node:Node, filename, label=None):
    dot = graph_node(node,label=label)
    dot.render(filename, view=False)
    dot.format = 'svg'
    dot.render(filename, view=False)
