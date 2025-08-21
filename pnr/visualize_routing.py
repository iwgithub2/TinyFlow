import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Import your DB classes to check item types
from db.Node import Node
from db.IOPort import IOPort

def visualize_routing(db, layers):
    """
    Creates an interactive 3D plot to visualize the placed and routed design.

    - Cells and I/O ports are shown as markers on the base layer.
    - Wire segments and vias for each net are drawn in a unique color.

    Args:
        db (TinyDB): The database containing the complete design.
        layers (list): The list of metal layer names, e.g., ['M1', 'M2', ...].
    """
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # --- 1. Setup Layers and Colors ---
    # Create a mapping from layer name to a z-coordinate (0, 1, 2...)
    layer_z_map = {name: i for i, name in enumerate(layers)}
    
    # --- MODIFICATION START ---
    # Get all nets to create a color mapping for them
    all_nets = db.get_all_nets()
    
    # Create a unique color for each NET
    colors = plt.cm.jet(np.linspace(0, 1, len(all_nets)))
    net_colors = {net_name: colors[i] for i, net_name in enumerate(all_nets.keys())}
    # --- MODIFICATION END ---
    
    print(f"Visualizing with layers: {list(layer_z_map.keys())}")

    # --- 2. Plot Placed Cells and I/O Ports ---
    cells_plotted = False
    ports_plotted = False
    for item_id, item in db.get_all_placeable_items().items():
        if item.is_placed():
            x, y = item.placement
            # Plot all components on the base layer (z=0) for reference
            if isinstance(item, Node):
                ax.scatter(x, y, 0, c='red', marker='s', s=100, label='Cells' if not cells_plotted else "")
                cells_plotted = True
            elif isinstance(item, IOPort):
                ax.scatter(x, y, 0, c='blue', marker='^', s=120, label='I/O Ports' if not ports_plotted else "")
                ports_plotted = True

    # --- 3. Plot the Routed Nets (Wires and Vias) ---
    for net_name, net in all_nets.items():
        # --- MODIFICATION START ---
        # Get the unique color for the current net
        color = net_colors.get(net_name)
        # --- MODIFICATION END ---

        # Plot Wire Segments
        for seg in net.wire_segments:
            x1, y1 = seg.start_point
            x2, y2 = seg.end_point
            z = layer_z_map.get(seg.layer)
            # The original 'layer_colors' is no longer used.
            if z is not None and color is not None:
                ax.plot([x1, x2], [y1, y2], [z, z], color=color, linewidth=2)

        # Plot Vias
        for via in net.vias:
            x, y = via.location
            z1 = layer_z_map.get(via.from_layer)
            z2 = layer_z_map.get(via.to_layer)
            if z1 is not None and z2 is not None and color is not None:
                # --- MODIFICATION START ---
                # Color the via with the net's color instead of a fixed gray
                ax.plot([x, x], [y, y], [z1, z2], color=color, linestyle='--', linewidth=1.5)
                # --- MODIFICATION END ---

    # --- 4. Configure Plot Aesthetics ---
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Metal Layer')
    
    # Set the Z-axis ticks and labels to be the layer names
    ax.set_zticks(list(layer_z_map.values()))
    ax.set_zticklabels(list(layer_z_map.keys()))

    # Set plot boundaries based on the die area
    x_min, y_min, x_max, y_max = db.die_area
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(0, len(layers))

    ax.set_title(f'3D Routing Visualization for "{db.name}"')
    ax.legend()
    
    # Improve viewing angle
    ax.view_init(elev=45, azim=-75)
    
    plt.show()