from algorithms.bfs import bfs_router
from algorithms.visualize import visualize_nets
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from db.TinyLef import TinyLef
from collections import defaultdict
from itertools import combinations

def simple_router(db : TinyDB, lib : TinyLib, lef : TinyLef):
    print("Running a simple router")

    # The key will be the pin name
    # The pin name = node_id_pin_name
    pin_locations = {}

    # Get the largest dimesion
    largest_length = 0
    largest_width = 0
    for cell in lef.cells.values():
        if cell.size[0] > largest_width:
            largest_width = cell.size[0]
        if cell.size[1] > largest_length:
            largest_length = cell.size[1]
    
    # 1. Convert the placement of the std cells into the new grid cooridnates
    for node_id in db.get_all_nodes():
        node = db.get_node_by_id(node_id)
        
        input_pins = node.input_pins
        output_pins = node.output_pin
        all_pins = input_pins.copy()
        all_pins.append(output_pins)

        bl_pos = node.placement
        node_type = node.cell_name

        # TODO figure out scaling and how to route pins..
        new_bl_pos = (bl_pos[0] * largest_width, bl_pos[1] * largest_length)

        # Calculate center position of each pin
        # Assume placement is bottom left corner
        for pin in all_pins:
            x_min, y_min, x_max, y_max = lef.cells[node_type].pins[pin]['ports'][0]['rect']
            new_id = node_id + "_" + pin
            pos = tuple(a + b for a, b in zip(( (x_min + x_min) / 2, (y_min + y_max) / 2 ), new_bl_pos)) + (0,)
            pin_locations[new_id] = pos

    # 2. Create Connections List
    connections = precise_db_parse_netlist(db)
    
    grid_dimen = db.get_die_area()
    new_grid_dimen = (grid_dimen[0] * largest_width, grid_dimen[1] * largest_length, grid_dimen[2] * largest_width, grid_dimen[3] * largest_length)
    nets = bfs_router(pin_locations, connections, new_grid_dimen, layers=5)

    visualize_nets(pin_locations, nets)


def precise_db_parse_netlist(db : TinyDB):
    netlist = db.get_netlist()

    # Store a dictionary where nets store all teh signals that are connected to the nets
    nets_to_pins = defaultdict(list)

    for cell_type, pin_dict, nodeid in netlist:
        for pin, net in pin_dict.items():
            nets_to_pins[net].append(f"{nodeid}_{pin}")
    
    connections = []
    for pins in nets_to_pins.values():
        if len(pins) > 1:
            for a, b in combinations(pins, 2):
                connections.append((a, b))

    return connections
