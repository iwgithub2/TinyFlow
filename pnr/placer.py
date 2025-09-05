from db.TinyDB import TinyDB
from itertools import combinations
from algorithms.visualize import visualize_placement, visualize_final_placement
from algorithms.simmulatedannealing import simulated_annealing
from collections import defaultdict
import sys

# Define
def simple_placement(db: TinyDB):
    netlist = db.get_netlist()

    # parse netlist
    connection_list = parse_db_netlist(netlist, db.get_inputs().union(db.get_outputs()))

    # Set grid size
    db.set_die_area(5, 5)
    grid_size = db.get_die_area() 

    finalplacement, cost, io_placement = simulated_annealing(
        db.get_all_nodes().keys(),
        connection_list,
        grid_size, 
        inputs=db.get_inputs(),
        outputs= db.get_outputs(), 
        use_gui=False
    )

    visualize_final_placement(finalplacement, connection_list, grid_size, cost)
    
    # Update Position
    for node in finalplacement.keys():
        x, y = finalplacement[node]
        db.set_node_placement(node, x, y)
    
    for io in io_placement:
        x, y = io_placement[io]
        db.set_port_placement(io, x, y)
    
def parse_db_netlist(netlist, io_ports):
    net_to_things = defaultdict(set)

    # Step 1 – map nets to the "things" (cells or io ports) that touch them
    for cell_type, pins, nodeid in netlist:
        for _, net in pins.items():
            net_to_things[net].add(nodeid)  # cell represented by nodeid
            if net in io_ports:
                net_to_things[net].add(net)  # io port represented by its name

    # Step 2 – create undirected connections
    connections = set()
    for things in net_to_things.values():
        if len(things) > 1:
            for a, b in combinations(sorted(things), 2):
                connections.add((a, b))

    return list(connections)

