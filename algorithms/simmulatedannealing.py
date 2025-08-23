
import random
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

import numpy as np
import matplotlib.pyplot as plt

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

def draw_arc(ax, x1, y1, x2, y2, color='red', lw=1.5):
  center_x = ((x1 + x2) / 2)
  center_y = ((y1 + y2) / 2)
  dx = x2 - x1
  dy = y2 - y1
  diameter = np.hypot(dx, dy)
  angle = np.degrees(np.arctan2(dy, dx))/2
  arc = patches.Arc((center_x, center_y), width=diameter, height=diameter,
            angle=angle, theta1=0, theta2=180, color=color, lw=lw)
  ax.add_patch(arc)

def draw_placement(ax, placement, nets, grid_size):
  ax.set_xlim(-1, grid_size+1)
  ax.set_ylim(-1, grid_size+1)
  # ax.set_aspect('equal')
  ax.axis('off')

  # Draw cells
  for cell, (x, y) in placement.items():
    ax.add_patch(patches.Rectangle((x, y), 1, 1,
                           edgecolor='black', facecolor='lightblue'))
    ax.text(x + 0.5, y + 0.5, cell, ha='center', va='center', fontsize=12)

  # Draw nets as shallow curves
  for net in nets:
    if len(net) == 2:
      cell1, cell2 = net
      x1, y1 = placement[cell1]
      x2, y2 = placement[cell2]
      draw_net(ax, x1+0.5, y1+0.5, x2+0.5, y2+0.5)

def visualize(current_placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size):
    fig, axes = plt.subplots(1, 3, figsize=(20, 5), gridspec_kw={'width_ratios': [1, 1, 2]} )
    fig.suptitle(f"Step {step} | Current Cost: {cost} | Best Cost: {best_cost}", fontsize=14)

    # --- Current Placement ---
    ax_current = axes[0]
    ax_current.set_title("Current Placement")
    draw_placement(ax_current, current_placement, nets, grid_size)

    # --- Best Placement ---
    ax_best = axes[1]
    ax_best.set_title("Best Placement")
    draw_placement(ax_best, best_placement, nets, grid_size)

    # --- Cost vs. Step Plot ---
    ax_cost = axes[2]
    ax_cost.set_title("Cost vs. Step")
    ax_cost.plot(cost_history, color='blue')
    ax_cost.set_xlabel("Step")
    ax_cost.set_ylabel("Cost")

    plt.tight_layout()
    plt.pause(0.001)

# def visualize(placement, nets, step, cost, grid_size):
#   fig, ax = plt.subplots(figsize=(6, 6))
#   ax.set_title(f"Step {step} | HPWL Cost = {cost}", fontsize=14)
#
#   # Draw cells
#   for cell, (x, y) in placement.items():
#     rect = patches.Rectangle((x, y), 1, 1, edgecolor='black', facecolor='lightblue')
#     ax.add_patch(rect)
#     ax.text(x + 0.5, y + 0.5, cell, ha='center', va='center', fontsize=12)
#
#   ax.set_xlim(0, grid_size)
#   ax.set_ylim(0, grid_size)
#   ax.set_xticks(range(grid_size + 1))
#   ax.set_yticks(range(grid_size + 1))
#   ax.grid(True)
#   ax.set_aspect('equal')
#   plt.pause(0.001)

def hpwl(placement, nets):
  total_cost = 0
  for net in nets:
    xs = [placement[cell][0] for cell in net]
    ys = [placement[cell][1] for cell in net]
    total_cost += (max(xs) - min(xs)) + (max(ys) - min(ys))
  return total_cost

def random_neighbor(placement, grid_size):
  new_placement = placement.copy()

  # randomly pick a cell to move
  cell1 = random.sample(list(new_placement.keys()), 1)[0]

  # randomly pick a site to considering moving cell to
  site_x = random.randint(0,grid_size-1)
  site_y = random.randint(0,grid_size-1)

  # see if there is already cell in the site, if so then swap cells

  found_cell = False
  for cell2, (x, y) in placement.items():
    if site_x == x and site_y == y:
      new_placement[cell1], new_placement[cell2] = new_placement[cell2], new_placement[cell1]
      found_cell = True

  # otherwise move cell to new site
  if not found_cell:
    new_placement[cell1] = (site_x,site_y)

  return new_placement

def simulated_annealing(cells, nets, grid_size, initial_temp=100.0, final_temp=0.05, alpha=0.98, max_iter=1000):
  positions = [(x, y) for x in range(grid_size) for y in range(grid_size)]
  random.shuffle(positions)
  placement = {cell: pos for cell, pos in zip(cells, positions)}
  cost = hpwl(placement, nets)
  T = initial_temp

  best_placement = placement.copy()
  best_cost = cost
  cost_history = []

  #visualize(best_placement, nets, 0, cost, grid_size)
  visualize(placement, best_placement, nets, 0, cost, best_cost, cost_history, grid_size)
  input("Press Enter to close...")
  plt.close()

  for step in range(max_iter):
    visualize(placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size)
    plt.close()

    new_placement = random_neighbor(placement, grid_size)
    new_cost = hpwl(new_placement, nets)
    cost_history.append(new_cost)
    delta = new_cost - cost

    if delta < 0 or random.random() < math.exp(-delta / T):
      placement = new_placement
      cost = new_cost
      if cost < best_cost:
        best_cost = cost
        best_placement = placement.copy()

    T *= alpha
    if T < final_temp:
      break

  visualize(placement, best_placement, nets, step, cost, best_cost, cost_history, grid_size)
  input("Press Enter to close...")
  plt.close()
  return best_placement, best_cost

# Define ring
cells = [chr(ord('A') + i) for i in range(16)]
nets = [[cells[i], cells[(i + 1) % len(cells)]] for i in range(len(cells))]

# Run the algorithm
grid_size = 8  # 4x4 grid
final_placement, final_cost = simulated_annealing(cells, nets, grid_size)
print("Final placement:", final_placement)
print("Final HPWL cost:", final_cost)