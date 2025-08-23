import heapq
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from db.Routing import Net
from pnr.placer import parse_db_netlist
from db.Node import *
import random
from collections import defaultdict
from pnr.visualize_routing import visualize_routing
import sys
import math

def simple_router(db : TinyDB, lib : TinyLib):
    print("Running a simple router")
    simple_a_star_router(
        db=db,
        lib=lib,
        grid_resolution=1.0,  
        layers=['M1', 'M2', 'M3', 'M4'],
        via_cost=2  # Make it 2x more expensive to change layer than to move 1 unit
    )

    all_nets = db.get_all_nets()
    for net_name, net_obj in all_nets.items():
        print(f"Net: {net_name} has {len(net_obj.wire_segments)} wires and {len(net_obj.vias)} vias.")
    
    visualize_routing(
        db=db,
        layers=['M1', 'M2', 'M3', 'M4'] # Ensure this matches the layers used in routing
    )

def simple_a_star_router(db, lib, grid_resolution=1.0, layers=['M1', 'M2', 'M3'], via_cost=5):
    """ """
    print("Starting Simple A* Router...")
    
    # --- 1. Setup ---
    x_min, y_min, x_max, y_max = db.die_area
    width_f  = (x_max - x_min) / grid_resolution
    height_f = (y_max - y_min) / grid_resolution
    # include the boundary node (fencepost) and avoid truncation
    grid_width  = int(math.ceil(width_f))  + 1
    grid_height = int(math.ceil(height_f)) + 1
    
    print(f"Routing on a {grid_width}x{grid_height} grid over {len(layers)} layers.")

    def pos_to_grid(pos):
        return (int(pos[0] / grid_resolution), int(pos[1] / grid_resolution))

    # These are blocked nodes
    obstacles = {}
    # These are blocked edges
    edges_dict = {}

    all_items = db.get_all_placeable_items()
    
    # This allows routing "over" cells on higher layers.
    for iid, item in all_items.items():
        if item.is_placed():
            gx, gy = pos_to_grid(item.placement)
            # block this (x,y) on ALL layers initially
            obstacles[iid] = {(gx, gy, L) for L in range(len(layers))}
    # This is used to prevent intersections
    obstacles['regular'] = set()
    netlist = db.get_netlist()
    connections = parse_db_netlist(netlist, lib)
    
    # Counts for when to unblock
    id_counts = defaultdict(int)
    for id1, id2 in connections:
        id_counts[id1] += 1
        id_counts[id2] += 1
    
    random.shuffle(connections)
    print(f"Found {len(connections)} connections to route.")
    
    routed_count = 0
    failed_count = 0
    for i, (source_id, dest_id) in enumerate(connections):
        print(f"\rRouting connection {i+1}/{len(connections)}...", end="")
        print(f"\nRouting connection {i+1}/{len(connections)}: {source_id[:8]}... -> {dest_id[:8]}...")

        source_item = all_items.get(source_id)
        dest_item = all_items.get(dest_id)

        # Shouldnt ever trigger this
        if not (source_item and source_item.is_placed() and dest_item and dest_item.is_placed()):
            continue
        
        start_gx, start_gy = pos_to_grid(source_item.placement)
        end_gx, end_gy = pos_to_grid(dest_item.placement)
        
        print(f"Starting: ({start_gx},{start_gy}), going to ({end_gx},{end_gy})")
        # Define start/goal points on the default first layer
        start_node = (start_gx, start_gy, 0)
        end_node = (end_gx, end_gy, 0)

        temp_obstacles = obstacles.copy()
        if source_id in temp_obstacles:
            del temp_obstacles[source_id]
        if dest_id in temp_obstacles:
            del temp_obstacles[dest_id]
        
        path = a_star_search(start_node, end_node, blocked_nodes=temp_obstacles, blocked_edges=edges_dict, layers=layers, via_cost=via_cost, grid=db.die_area)

        if path:
            # Reduce connections needed for a cell
            id_counts[source_id] -= 1
            id_counts[dest_id] -= 1

            # Remove "Blocked nodes" which is technically space above
            if id_counts[source_id] <= 0:
                del obstacles[source_id]
            if id_counts[dest_id] <= 0:
                del obstacles[dest_id]

            # We need to add a net to this 
            net_name = f"net_{source_id[:4]}_{dest_id[:4]}_{i}"
            new_net = Net(net_name)

            # We need to update the edge dictionary
            # Iterate through the path
            for j in range(len(path) - 1):
                p1, p2 = path[j], path[j+1]

                # Convert path back to real coordinates for storage
                p1_real = (p1[0] * grid_resolution, p1[1] * grid_resolution)
                p2_real = (p2[0] * grid_resolution, p2[1] * grid_resolution)
                
                # Update the edge dictionary twice because it is adjacency (doesnt store blocked nodes)
                # Via, update blocked node
                if p1[2] != p2[2]:
                    new_net.add_via(p1_real, layers[min(p1[2], p2[2])], layers[max(p1[2], p2[2])])
                    # For now we dont care about vias.. we allow multiple vias in a node......
                # Regular Segment
                else: 
                    # First instantiate if it doesnt exist
                    add_edge(edges_dict=edges_dict, p1=p1, p2=p2, capacity=1)
                    # Increment Edges
                    if not increment_edge(edges_dict=edges_dict, p1=p1, p2=p2):
                        raise ValueError("This error should never happen that means there is a bug because we are trying to increment when edges are full")
                    # we need to block the node as long as it is not an pin..
                    if p1 != start_node:
                        obstacles['regular'].add(p1)
                    if p2 != end_node:
                        obstacles['regular'].add(p2)

                    new_net.add_wire_segment(layers[p1[2]], p1_real, p2_real, width=grid_resolution/2)
            
            # Store the route
            db.add_net(new_net)
            routed_count += 1
            print(f"  -> Success! Path length: {len(path)} \n")
        else:
            failed_count += 1
            print(f"  -> FAILED to find a route for connection.\n")

    print() # Final newline for the progress indicator
    print(f"Routing complete. {routed_count} nets routed, {failed_count} failed.")
    print("Obstacles: ", obstacles)

######################################
# Code for Managing the edge dictonary
######################################

def add_edge(edges_dict, p1, p2, capacity=1):
    """Ensure edge (p1 <-> p2) exists with given capacity."""
    # Safe lookup: if not present, add it
    if p1 not in edges_dict:
        edges_dict[p1] = {}
    if p2 not in edges_dict[p1]:
        edges_dict[p1][p2] = {'capacity': capacity, 'used': 0}
    
    if p2 not in edges_dict:
        edges_dict[p2] = {}
    if p1 not in edges_dict[p2]:
        edges_dict[p2][p1] = {'capacity': capacity, 'used': 0}

def increment_edge(edges_dict, p1, p2):
    """Try to increment edge usage if not full."""
    if not is_full(edges_dict, p1, p2):  # safe check
        edges_dict[p1][p2]['used'] += 1
        edges_dict[p2][p1]['used'] += 1
        return True
    return False

def is_full(edges_dict, p1, p2):
    """Return True if edge is full, False otherwise (safe lookup)."""
    cap = edges_dict.get(p1, {}).get(p2, {}).get('capacity')
    used = edges_dict.get(p1, {}).get(p2, {}).get('used')
    
    if cap is None or used is None:
        return False  # edge doesn't exist → not full
    
    return used >= cap

# --- The A* Router ---

def heuristic(a, b):
    """Calculate 3D Manhattan distance for the A* heuristic."""
    (x1, y1, z1) = a
    (x2, y2, z2) = b
    # Give a slight penalty to layer changes in the heuristic
    return abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2) * 2

def a_star_search(start, goal, blocked_nodes, blocked_edges, layers, via_cost, grid):
    """
    start: (x, y, z)
    goal: (x, y, z)
    """
    open_set = []

    # Adding to our list in a heap like way
    # Each item is based on (cost, coordinates) so (cost, (x, y))
    # The heap is ordered by the first element of the tuple
    heapq.heappush(open_set, (0, start))

    # Keeps track of the path
    came_from = {}

    # Actual Current Cost
    g_score = {start: 0}

    # Heuristic cost used to guide the A*
    f_score = {start: heuristic(start, goal)}

    nodes_explored = 0
    x_min, y_min, x_max, y_max = grid
    
    while open_set:
        # Get the lowest cost coordinate/point
        _, current = heapq.heappop(open_set)
        nodes_explored += 1
        
        if current == goal:
            print(f"    -> A* Success! Explored {nodes_explored} nodes.")
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            # Return reveresed list for correct path
            return path[::-1]
        
        x, y, z = current
        potential_neighbors = [(x+1, y, z), (x-1, y, z), (x, y+1, z), (x, y-1, z)]
        if z > 0: potential_neighbors.append((x, y, z-1))
        if z < len(layers) - 1: potential_neighbors.append((x, y, z+1))
        
        neighbors = []
        # Iterate through potential neighbors and add valid neighbors
        for nx, ny, nz in potential_neighbors:
            if x_min <= nx < x_max and y_min <= ny < y_max:
                neighbors.append((nx, ny, nz))
        
        for neighbor in neighbors:
            # If the node is occupied check other neighbors
            # We check to makesure its not covering space above an unrouted std cell
            # We check to make sure we arent going through a node a path has already been through
            # We need to check to make sure we arent going through a node that is a a std cell
            if neighbor in blocked_nodes.values() or neighbor in blocked_nodes['regular']:
                continue
            # If the edge is blocked we need to consider other neighbors
            if is_full(edges_dict=blocked_edges, p1=current, p2=neighbor):
                continue
            # Determine move cost chceks if the z of the neightbor z coordinate are not equal
            move_cost = via_cost if neighbor[2] != z else 1

            # Calculate its real cost
            tentative_g_score = g_score[current] + move_cost
            
            # If we dont know the score of the neighbor or the score is somehow lower (could be a different path)
            # Add teh score the list
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    print(f"    -> A* FAILED. Explored {nodes_explored} nodes.")
    return None