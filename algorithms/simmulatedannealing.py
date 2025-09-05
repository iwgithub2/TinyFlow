import random
from algorithms.visualize import visualize_placement
import matplotlib.pyplot as plt
import math

def simulated_annealing(cells, nets, grid_size, inputs, outputs, use_gui=False, initial_temp=100.0, final_temp=0.05, alpha=0.98, max_iter=1000): 
    # Place IO pads
    io_placement = place_io(inputs, outputs, grid_size)   

    minus_x, minus_y, pos_x, pos_y = grid_size
    positions = [(x, y) for x in range(minus_x, pos_x) for y in range(minus_y, pos_y)]
    random.shuffle(positions)
    
    cell_placement = {cell: pos for cell, pos in zip(cells, positions)}
    
    placement = {**cell_placement, **io_placement}

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
            visualize_placement(fig, axes, placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size)
            plt.pause(0.01) # Pause to allow plot to update

        new_placement = random_neighbor(placement, grid_size, fixed=io_placement.keys())
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
        visualize_placement(fig, axes, placement, best_placement, nets, step + 1, cost, best_cost, cost_history, grid_size)
        plt.ioff() # Turn off interactive mode
        print("GUI finished. Press Enter in the console or close the plot window to continue.")
        plt.show() # Show final plot and block until closed

    return best_placement, best_cost, io_placement

def hpwl(placement, nets):
    total_cost = 0
    for net in nets:
        xs = [placement[cell][0] for cell in net]
        ys = [placement[cell][1] for cell in net]
        total_cost += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return total_cost

def random_neighbor(placement, grid_size, fixed=set()):
    minus_x, minus_y, pos_x, pos_y = grid_size
    new_placement = placement.copy()
  
    # randomly pick a NON-fixed cell
    movable_cells = [c for c in placement if c not in fixed]
    if not movable_cells:
        return new_placement

    cell1 = random.choice(movable_cells)

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

