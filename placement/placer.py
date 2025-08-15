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

# Define
def simple_placement(db_mapped: TinyDB, lib : TinyLib):
    netlist = db_mapped.get_netlist()
    print("Db:", db_mapped.vars)
    # print("Netlist:", netlist)

    # parse netlist
    gates_count, connection_list, gates = parse_db_netlist(netlist, lib)
    print("Gates Count:", gates_count)
    print("Connections:", connection_list)
    print("Gates:", gates)

    # grid_size = 10 # 10x10 grid
    
    # finalplacement, cost = simulated_annealing(gates, connection_list, grid_size, use_gui=False)

    # print("Final placement:", finalplacement)
    # print("Final cost:", cost)

    # visualize_final_placement(finalplacement, connection_list, grid_size, cost)
    # update_nodes_with_placement(db_mapped, finalplacement)

def parse_db_netlist(netlist, lib):
    """
    Parses a netlist to extract a list of cells
    and an array containing pairs which are connections
    E.g. 
    Cells: ['A', 'B', 'C']
    Nets: [('A', 'B'), ('B', 'C')] 

    This would demonstrate cells A B and C, with B connected to A and C
    """

    wire_to_gate_map = {}
    gates = {}
    gate_counter = {}

    for gate_info in netlist:
        gate_type, connections = gate_info
        
        if gate_type not in gate_counter:
            gate_counter[gate_type] = 0
        
        instance_name = f"{gate_type}_{gate_counter[gate_type]}"
        gate_counter[gate_type] += 1
        gates[instance_name] = {'type': gate_type}

        # Get output pin name
        output_pin = lib.cells[gate_type].output_pin

        for port, wire in connections.items():
            if wire not in wire_to_gate_map:
                wire_to_gate_map[wire] = {'output_of': None, 'input_to': []}
            if port == output_pin:
                wire_to_gate_map[wire]['output_of'] = instance_name
            else:
                wire_to_gate_map[wire]['input_to'].append(instance_name)
    
    connections_list = []
    for wire, connected_gates in wire_to_gate_map.items():
        source_gate = connected_gates.get('output_of')
        if source_gate:
            for destination_gate in connected_gates.get('input_to', []):
                connections_list.append((source_gate, destination_gate))

    
    return gate_counter, connections_list, list(gates.keys())

def update_nodes_with_placement(db, final_placement):
    """
    Updates Node objects in a TinyDB with their final placement and size info.

    Args:
        db (TinyDB): The database containing the original Node objects.
        final_placement (dict): The output from the annealer. 
                                Maps {output_wire_name: (x, y)}.
        final_cell_sizes (dict): The final sizes of the cells.
                                Maps {output_wire_name: (width, height)}.
    """
    print("\n--- Updating TinyDB Nodes with Placement Data ---")
    
    updated_nodes_set = set()

    def _recursive_update(name, node):
        """
        An inner helper function to perform the depth-first update.
        """
        if node in updated_nodes_set:
            return 0
        
        updated_nodes_set.add(node)
        print("Node: ", name, " is node type: ", node)
        # The unique name for a placed cell is its output signal wire name.
        # This is the key that links the logical Node to the physical cell.
        instance_name = node.output_signal
        
        nodes_updated_count = 0
        
        # --- Action: Update the current node ---
        if instance_name in final_placement:
            # Get the placement and size results for this node
            x_coord, y_coord = final_placement[instance_name]
            
            # Update the node object's physical attributes
            node.x = x_coord
            node.y = y_coord
            
            # CRITICAL: Update the node's state to reflect the design flow stage
            node.state = Node.State.POST_PLACE
            
            nodes_updated_count = 1 # We successfully updated one node
            # print(f"  -> Updated node for wire '{instance_name}': Pos=({x_coord},{y_coord}), State={node.state.name}")
        else:
            # This can happen if a node was optimized away during a previous step
            # or is part of an unmapped logical tree.
            # print(f"  -> Warning: Node for wire '{instance_name}' not found in placement results. Skipping.")
            pass

        # --- Recursive Step: Traverse to children ---
        for child in node.children:
            if isinstance(child, Node):
                nodes_updated_count += _recursive_update(child.cell_name, child)
                
        return nodes_updated_count

    # --- Main Logic: Start the recursion from all roots in the database ---
    total_updated = 0
    for var_name, root_node in db.vars.items():
        if isinstance(root_node, Node):
            total_updated += _recursive_update(root_node.cell_name, root_node)
            
    print(f"\nSuccessfully updated {total_updated} nodes to the POST_PLACE state.")

def hpwl(placement, nets):
    total_cost = 0
    for net in nets:
        xs = [placement[cell][0] for cell in net]
        ys = [placement[cell][1] for cell in net]
        total_cost += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return total_cost

def random_neighbor(placement, grid_size):
    half_size = grid_size // 2
    new_placement = placement.copy()

    # randomly pick a cell to move
    cell1 = random.choice(list(new_placement.keys()))

    # pick a random target location in centered coordinates
    site_x = random.randint(-half_size, half_size - 1)
    site_y = random.randint(-half_size, half_size - 1)

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
    half_size = grid_size // 2
    positions = [(x, y) for x in range(-half_size, half_size) for y in range(-half_size, half_size)]
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
    half_size = grid_size // 2

    # Axis limits in centered coords
    ax.set_xlim(-half_size - 0.5, half_size - 0.5)
    ax.set_ylim(-half_size - 0.5, half_size - 0.5)
    ax.set_aspect('equal')

    # Grid lines
    ax.set_xticks(np.arange(-half_size - 0.5, half_size + 0.5, 1))
    ax.set_yticks(np.arange(-half_size - 0.5, half_size + 0.5, 1))
    ax.grid(True, which='major', color='gray', linestyle='--', linewidth=0.5)

    # Show coordinate numbers
    ax.set_xticklabels(np.arange(-half_size, half_size + 1, 1))
    ax.set_yticklabels(np.arange(-half_size, half_size + 1, 1))

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