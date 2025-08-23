import random
import math
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
import numpy as np
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from db.LogicNodes import INV, AND, NAND, OR, NOR, XOR, XNOR
from db.Node import Node
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# Define
def simple_placement(db: TinyDB, lib : TinyLib):
    netlist = db.get_netlist()

    # parse netlist
    connection_list = parse_db_netlist(netlist, lib)

    # Set grid size
    db.set_die_area(5, 5)
    grid_size = db.get_die_area() 
    
    # Place IO pads
    io_placement = place_io(db.get_inputs(), db.get_outputs(), grid_size)
    for io in io_placement:
        x, y = io_placement[io]
        db.set_port_placement(io, x, y)
    
    finalplacement, cost = simulated_annealing(db.get_all_nodes().keys(), connection_list, grid_size, use_gui=True)

    visualize_final_placement(finalplacement, connection_list, grid_size, cost)
    # Update Position
    for node in finalplacement.keys():
        x, y = finalplacement[node]
        db.set_node_placement(node, x, y)
    
    # print(len(db.get_placed_nodes().keys()))

def parse_db_netlist(netlist, lib):
    """
    Parses a netlist to create a list of connections (nets) between gates.
    Each connection is a tuple of (source_node_id, destination_node_id).

    Args:
        netlist (list): A list of tuples, where each tuple is
                        (gate_type, node_id, connections_dict).
        lib (TinyLib): The technology library, used to find output pin names.

    Returns:
        list: A list of tuples representing the connections (nets)
              between gate IDs, e.g., [(source_id, dest_id)].
    """
    wire_to_gate_map = {}

    # 1. First pass: Build a map of each wire to its driving gate (output_of)
    #    and its fan-out gates (input_to).
    for gate_type, connections, node_id in netlist:
        try:
            output_pin = lib.cells[gate_type].output_pin
        except KeyError:
            # This handles cases where a cell in the netlist isn't in the library
            raise ValueError(f"Gate type '{gate_type}' (ID: {node_id}) not found in the library.")

        for port, wire in connections.items():
            # Initialize the wire entry if it's the first time we see it
            if wire not in wire_to_gate_map:
                wire_to_gate_map[wire] = {'output_of': None, 'input_to': []}
            
            if port == output_pin:
                wire_to_gate_map[wire]['output_of'] = node_id
            else:
                wire_to_gate_map[wire]['input_to'].append(node_id)

    # 2. Second pass: Use the map to create the list of (source, destination) pairs.
    connections_list = []
    for wire, connected_gates in wire_to_gate_map.items():
        source_id = connected_gates.get('output_of')
        
        # A valid net must have a source gate.
        if source_id:
            for destination_id in connected_gates.get('input_to', []):
                connections_list.append((source_id, destination_id))
    
    return connections_list

def place_io(input_pins, output_pins, grid_size):
    """
    Simple IO pin placement. 
    This version will place all input_pins randomly in order on a line on the left side
    and place all output_pins randomly in order on a line on the right side

    input_pins: set()
    output_pins: set()
    grid_size: (-x, x, -y, y)

    Returns a dictonary of the coordinates of each pin
    """
    
    x_left = grid_size[0] - 1
    x_right = grid_size[2] + 1

    input_pins = list(input_pins)
    output_pins = list(output_pins)
    
    random.shuffle(input_pins)
    random.shuffle(output_pins)
    # space evenly and constrain wiht cost
    io_placement = {}

    top_l = math.floor(len(input_pins) / 2)

    for i, pin in enumerate(input_pins):
        io_placement[pin] = (x_left, top_l - i)
    
    top_r = math.floor(len(output_pins) / 2)

    for i, pin in enumerate(output_pins):
        io_placement[pin] = (x_right, top_r - i)

    return io_placement
     
def hpwl(placement, nets):
    total_cost = 0
    for net in nets:
        xs = [placement[cell][0] for cell in net]
        ys = [placement[cell][1] for cell in net]
        total_cost += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return total_cost

def random_neighbor(placement, grid_size):
    minus_x, minus_y, pos_x, pos_y = grid_size
    new_placement = placement.copy()

    # randomly pick a cell to move
    cell1 = random.choice(list(new_placement.keys()))

    # pick a random target location in centered coordinates
    site_x = random.randint(minus_x, pos_x - 1)
    site_y = random.randint(minus_y, pos_y - 1)

    # see if there is already cell in the site, if so then swap cells
    found_cell = False
    for cell2, (x, y) in placement.items():
        if site_x == x and site_y == y:
            new_placement[cell1], new_placement[cell2] = new_placement[cell2], new_placement[cell1]
            found_cell = True
            break

    if not found_cell:
        new_placement[cell1] = (site_x, site_y)

    return new_placement

def simulated_annealing(cells, nets, grid_size, use_gui=False, initial_temp=100.0, final_temp=0.05, alpha=0.98, max_iter=1000):
    minus_x, minus_y, pos_x, pos_y = grid_size
    positions = [(x, y) for x in range(minus_x, pos_x) for y in range(minus_y, pos_y)]
    random.shuffle(positions)
    placement = {cell: pos for cell, pos in zip(cells, positions)}
    cost = hpwl(placement, nets)
    T = initial_temp

    best_placement = placement.copy()
    best_cost = cost
    cost_history = []

    fig, axes = None, None
    if use_gui:
            plt.ion() # Turn on interactive mode
            fig, axes = plt.subplots(1, 3, figsize=(20, 5), gridspec_kw={'width_ratios': [1, 1, 2]})

    step = 0
    for step in range(max_iter):
        if use_gui:
            # Update the visualization on the existing plot
            visualize(fig, axes, placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size)
            plt.pause(0.01) # Pause to allow plot to update

        new_placement = random_neighbor(placement, grid_size)
        new_cost = hpwl(new_placement, nets)
        
        delta = new_cost - cost

        if delta < 0 or random.random() < math.exp(-delta / T):
            placement = new_placement
            cost = new_cost
            if cost < best_cost:
                best_cost = cost
                best_placement = placement.copy()

        cost_history.append(cost) # Track cost history
        T *= alpha
        if T < final_temp:
            break

    if use_gui:
        # Final visualization
        visualize(fig, axes, placement, best_placement, nets, step + 1, cost, best_cost, cost_history, grid_size)
        plt.ioff() # Turn off interactive mode
        print("GUI finished. Press Enter in the console or close the plot window to continue.")
        plt.show() # Show final plot and block until closed

    return best_placement, best_cost

def draw_net(ax, x1, y1, x2, y2, curvature=0.3, color='red', lw=1.5):
    # Calculate the midpoint
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    # Calculate the direction vector from start to end
    dx, dy = x2 - x1, y2 - y1
    # Calculate the perpendicular (normal) vector
    nx, ny = -dy, dx
    # Normalize the normal vector
    length = np.hypot(nx, ny)
    if length == 0:
        return  # Avoid division by zero
    nx, ny = nx / length, ny / length

    # Determine the control point for the Bézier curve
    cx, cy = mx + curvature * nx, my + curvature * ny

    # Generate points along the Bézier curve
    t = np.linspace(0, 1, 100)
    bezier_x = (1 - t)**2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
    bezier_y = (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2

    # Plot the curve
    ax.plot(bezier_x, bezier_y, color=color, lw=lw)

    # Add red dots at the start and end points
    ax.plot([x1, x2], [y1, y2], 'ro', markersize=4)

def draw_placement(ax, placement, nets, grid_size):
    """
    We draw the placement of the cells shifted on a grid so it lines up nicely. The coordinates represent the center of each cell.
    """
    ax.clear()
    minus_x, minus_y, pos_x, pos_y = grid_size

    # Axis limits in centered coords
    ax.set_xlim(minus_x - 0.5, pos_x - 0.5)
    ax.set_ylim(minus_y - 0.5, pos_y - 0.5)
    ax.set_aspect('equal')

    # Grid lines
    ax.set_xticks(np.arange(minus_x - 0.5, pos_x + 0.5, 1))
    ax.set_yticks(np.arange(minus_y - 0.5, pos_y + 0.5, 1))
    ax.grid(True, which='major', color='gray', linestyle='--', linewidth=0.5)

    # Show coordinate numbers
    ax.set_xticklabels(np.arange(minus_x, pos_x + 1, 1))
    ax.set_yticklabels(np.arange(minus_y, pos_y + 1, 1))

    # Draw cells (no shift needed now)
    for cell, (x, y) in placement.items():
        ax.add_patch(patches.Rectangle((x - 0.5, y - 0.5), 1, 1, edgecolor='black', facecolor='lightblue'))
        ax.text(x, y, cell, ha='center', va='center', fontsize=8)

    # Draw nets
    for net in nets:
        if len(net) == 2:
            cell1, cell2 = net
            x1, y1 = placement[cell1]
            x2, y2 = placement[cell2]
            draw_net_curve(ax, x1, y1, x2, y2)

def draw_net_curve(ax, x1, y1, x2, y2, color='red', lw=1.5):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    nx, ny = -dy, dx
    length = np.hypot(nx, ny)
    if length == 0: return
    nx, ny = nx / length, ny / length
    cx, cy = mx + 0.3 * nx, my + 0.3 * ny
    t = np.linspace(0, 1, 100)
    bezier_x = (1 - t)**2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
    bezier_y = (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
    ax.plot(bezier_x, bezier_y, color=color, lw=lw)
    ax.plot([x1, x2], [y1, y2], 'ro', markersize=4)

def visualize(fig, axes, current_placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size):
    fig.suptitle(f"Step {step} | Current Cost: {cost:.2f} | Best Cost: {best_cost:.2f}", fontsize=16)

    draw_placement(axes[0], current_placement, nets, grid_size)
    axes[0].set_title("Current Placement")

    draw_placement(axes[1], best_placement, nets, grid_size)
    axes[1].set_title("Best Placement")

    # This also clears the cost subplot before redrawing the line graph
    axes[2].clear() 
    axes[2].set_title("Cost vs. Step")
    axes[2].plot(cost_history, color='blue')
    axes[2].set_xlabel("Step")
    axes[2].set_ylabel("Cost")
    axes[2].grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

def visualize_final_placement(placement, nets, grid_size, cost):
    """
    Creates a single, static plot of the final placement.
    """
    # Create a new figure with a single subplot
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Use our existing drawing function to render the placement
    draw_placement(ax, placement, nets, grid_size)
    
    # Set a clear title
    ax.set_title(f"Final Placement (Cost: {cost:.2f})", fontsize=16)
    
    # Display the plot. The program will pause here until the window is closed.
    plt.show()