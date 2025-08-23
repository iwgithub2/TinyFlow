import collections
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def bfs_router(coordinates_dict, connection_list, grid_dimen, layers=1):
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
    for id1, id2 in connections:
        id_counts[id1] += 1
        id_counts[id2] += 1
    
    shuffled_keys = list(coordinates_dict.keys())
    random.shuffle(shuffled_keys)
    
    routed_count = 0
    failed_count = 0
    for i, (source_id, dest_id) in enumerate(connections):
        source_pos = coordinates_dict[source_id]
        dest_pos = coordinates_dict[dest_id]

        temp_obstacles = obstacles.copy()
        if source_id in temp_obstacles:
            del temp_obstacles[source_id]
        if dest_id in temp_obstacles:
            del temp_obstacles[dest_id]
        
        # Path should be a list of nodes (coordinates) that is being used to reach the dest
        path = bfs_search(source_pos, dest_pos, blocked_nodes=temp_obstacles, layers=layers, grid=grid_dimen, nodes=nodes)

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

def bfs_search(start, goal, blocked_nodes, layers, grid, nodes):
    """
    start: (x, y, z)
    goal: (x, y, z)
    """
    queue  = collections.deque([start])

    came_from = {start : None}

    nodes_explored = 0
    x_min, y_min, x_max, y_max = grid
    
    while queue:
        current = queue.popleft()
        nodes_explored += 1

        if current in nodes and current != start and current != goal:
            continue
        
        if current == goal:
            print(f"    -> BFS Success! Explored {nodes_explored} nodes.")
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
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
            
            # If we dont know the score of the neighbor or the score is somehow lower (could be a different path)
            # Add teh score the list
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    print(f"    -> BFS* FAILED. Connection {start} to {goal} failed. Explored {nodes_explored} nodes.")
    return None

def visualize_nets(points, routed_nets, title="3D Net Visualization"):
    """
    Plots a 3D visualization of points and their routed paths.

    Args:
        points (dict): A dictionary where keys are point IDs (e.g., 'A') and 
                       values are 3D coordinates (x, y, z).
        routed_nets (dict): A dictionary where keys are tuples representing
                            the start and end points of a net (e.g., ('A', 'H')),
                            and values are a list of intermediate points that make up
                            the routed path.
        title (str): The title for the plot.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # --- Plot the routed nets ---
    # We will iterate through the routed_nets dictionary to draw each path.
    # Each path is a list of points (tuples of coordinates).
    print("Plotting routed nets...")
    for net_id, path in routed_nets.items():
        # Unzip the coordinates into separate x, y, z lists for plotting
        x_coords = [p[0] for p in path]
        y_coords = [p[1] for p in path]
        z_coords = [p[2] for p in path]
        
        # Plot the path as a line. Use different markers and styles for clarity.
        ax.plot(x_coords, y_coords, z_coords, marker='o', linestyle='-', label=f"Net {net_id[0]}-{net_id[1]}")

    # --- Plot the individual points ---
    # We plot all the nodes, regardless of whether they are on a path or not.
    print("Plotting all individual points...")
    x_points = [p[0] for p in points.values()]
    y_points = [p[1] for p in points.values()]
    z_points = [p[2] for p in points.values()]
    
    # Plot the points as markers. We use 'o' for circles.
    ax.scatter(x_points, y_points, z_points, c='black', s=100)

    # Add text labels to each point for easy identification
    for point_id, coords in points.items():
        ax.text(coords[0], coords[1], coords[2], point_id, fontsize=12, ha='right')

    # --- Set plot properties ---
    ax.set_title(title)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')

    # Add a legend to show which line corresponds to which net
    ax.legend()
    
    # Display the plot
    plt.show()

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
    nets = bfs_router(points, connections, (-10, -10, 10, 10), layers=4)
    print("Nets: ", nets)
    visualize_nets(points, nets)