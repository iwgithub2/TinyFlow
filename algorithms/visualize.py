import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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