import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

#################################################
# Placement
#################################################

def visualize_placement(fig, axes, current_placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size):
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

#################################################
# Routing
#################################################

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