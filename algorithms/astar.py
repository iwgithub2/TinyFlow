import heapq
import collections
import random
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from algorithms.visualize import visualize_nets

def a_star_router(coordinates_dict, connection_list, grid_dimen, layers=1):
    """ 
    coordinates_dict : Dictionary where keys will be a node (specific position of a pin) and the value is a tuple (x, y, z)
    connection_list : List of tuples where each tuple is a pair of ids of pins that need to be connected
    layers : How many vertical layers we want
    grid_dimen : Tuple for the grid size: (x_min, y_min, x_max, y_max)
    """    
    # --- 1. Setup ---
    x_min, y_min, x_max, y_max = grid_dimen

    # These are blocked nodes
    # Store the node ids as the key, 
    # All other regular blocked nodes are under the key 'regular'
    obstacles = {}
    
    nodes = coordinates_dict.values()

    # Routed Nets
    # The key will be a tuple from the connection list and the value will be a list of the net
    routed_nets = {}

    # This allows routing "over" cells on higher layers.
    for key in coordinates_dict:
        # pz should be zero... Im not sure what happens when it isnt
        px, py, pz = coordinates_dict[key]
        obstacles[key] = {(px, py, L) for L in range(layers)}

    # This is used to prevent intersections
    obstacles['regular'] = set()

    # This wont deal with fanout right now but lets leave this for now   
    # Counts for when to unblock
    id_counts = collections.defaultdict(int)
    for id1, id2 in connection_list:
        id_counts[id1] += 1
        id_counts[id2] += 1
    
    shuffled_keys = list(coordinates_dict.keys())
    random.shuffle(shuffled_keys)
    
    routed_count = 0
    failed_count = 0
    for i, (source_id, dest_id) in enumerate(connection_list):
        source_pos = coordinates_dict[source_id]
        dest_pos = coordinates_dict[dest_id]

        temp_obstacles = obstacles.copy()
        if source_id in temp_obstacles:
            del temp_obstacles[source_id]
        if dest_id in temp_obstacles:
            del temp_obstacles[dest_id]
        
        # Path should be a list of nodes (coordinates) that is being used to reach the dest
        path = a_star_search(source_pos, dest_pos, blocked_nodes=temp_obstacles, layers=layers, grid=grid_dimen, nodes=nodes)

        if path:
            # Reduce connections needed for a cell
            id_counts[source_id] -= 1
            id_counts[dest_id] -= 1

            # Remove "Blocked nodes" which is technically space above
            if id_counts[source_id] <= 0:
                del obstacles[source_id]
            if id_counts[dest_id] <= 0:
                del obstacles[dest_id]
            
            # Write to our routed nets
            routed_nets[(source_id, dest_id)] = path

            # We need to update the blocked nodes
            # Iterate through the path
            for node in path:
                obstacles['regular'].add(node)
            
            # Store the route
            routed_count += 1
            print(f"  -> Success! Path length: {len(path)} \n")
        else:
            failed_count += 1
            print(f"  -> FAILED to find a route for connection.\n")

    print() # Final newline for the progress indicator
    print(f"Routing complete. {routed_count} nets routed, {failed_count} failed.")

    return routed_nets

def heuristic(point_a, point_b):
    """
    Calculates the Manhattan distance heuristic between two 3D points.
    """
    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1]) + abs(point_a[2] - point_b[2])

def a_star_search(start, goal, blocked_nodes, layers, grid, nodes, via_cost=5):
    """
    start         : (x, y, z)
    goal          : (x, y, z)
    blocked_nodes : dictionary 
    layers        : Number of layers
    grid          : Tuple for the grid size: (x_min, y_min, x_max, y_max)
    nodes         : Nodes of the pins which are allowed to be reused at start and end but not throughout
    """
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))

    came_from = {start : None}

    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    nodes_explored = 0
    x_min, y_min, x_max, y_max = grid
    
    while open_set:
        current_f_score, current = heapq.heappop(open_set)
        nodes_explored += 1

        # Skip this node if it's a pin node that isn't the start or goal
        if current in nodes and current != start and current != goal:
            continue
        
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
        if z < layers - 1: potential_neighbors.append((x, y, z+1))
        
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
            
            move_cost = via_cost if neighbor[2] != z else 1
            tentative_g_score = g_score[current] + move_cost

            # If we dont know the score of the neighbor or the score is somehow lower (could be a different path)
            # Add teh score the list
            if tentative_g_score < g_score.get(neighbor, math.inf):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                # Push the neighbor to the priority queue
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    print(f"    -> A* FAILED. Connection {start} to {goal} failed. Explored {nodes_explored} nodes.")
    return None

if __name__ == "__main__":
    points = {
        'A': (0, 0, 0),
        'B': (-1, 0, 1),
        'C': (0, 1, 1),
        'D': (1, 2, 0),
        'E': (0, 2, 0),
        'F': (3, 0, 1),
        'G': (-1, 1, 0),
        'H': (1, -2, 2)
    }
    connections = [
        ('A', 'B'),
        ('A', 'C'),
        ('A', 'E'),
        ('B', 'D'),
        ('B', 'F'),
        ('C', 'D'),
        ('C', 'G'),
        ('D', 'H'),
        ('E', 'F'),
        ('E', 'G'),
        ('F', 'H'),
        ('G', 'H')
    ]
    nets = a_star_router(points, connections, (-10, -10, 10, 10), layers=4)
    print("Nets: ", nets)
    visualize_nets(points, nets)