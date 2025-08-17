import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from itertools import permutations
import math
from multiprocessing import reduction
from utils.PrettyStream import *
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from db.Node import Node
from db.LogicNodes import *

# Global animation log
tech_map_steps = []

# Modified tech_map with animation hooks
def tech_map(node, lib, top_node=True, out=None):
    if node.optimal_match is not None:
        return node.optimal_match

    best_cost = math.inf
    best_tree = None

    for cell_name, cell in lib.cells.items():
        for p in cell.patterns:
            cost = lib.cell_costs[cell_name]
            result = match_pattern(node, p)
            step = {
                'node': node,
                'cell': cell_name,
                'pattern': p,
                'matched': False,
                'children': node.children
            }

            if result is None:
                tech_map_steps.append(step)
                continue

            match_cost = cost
            subtrees = {}
            for port, wire in result.items():
                if isinstance(wire, Node):
                    m, c = tech_map(wire, lib, top_node=False, out=wire.output_signal)
                    match_cost += c
                    subtrees[port] = m
                else:
                    subtrees[port] = wire

            tree = cell(*[subtrees[pin] for pin in cell.input_pins], out=out)
            step.update({
                'matched': True,
                'tree': tree,
                'cost': match_cost
            })
            tech_map_steps.append(step)

            if match_cost < best_cost:
                best_tree = tree
                best_cost = match_cost

    node.optimal_match = best_tree, best_cost
    return best_tree, best_cost

# GUI to animate mapping steps
class MappingAnimator(tk.Tk):
    def __init__(self, steps):
        super().__init__()
        self.title("Technology Mapping Animation")
        self.geometry("1000x600")
        self.steps = steps
        self.index = 0

        self.create_widgets()
        self.draw_step()

    def create_widgets(self):
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill='both', expand=True)

        controls = ttk.Frame(self)
        controls.pack()

        self.step_label = ttk.Label(controls, text=f"Step 0 / {len(self.steps)}")
        self.step_label.pack(side='left')

        ttk.Button(controls, text="< Prev", command=self.prev_step).pack(side='left')
        ttk.Button(controls, text="Next >", command=self.next_step).pack(side='left')
        ttk.Button(controls, text="Play", command=self.play).pack(side='left')

        self.speed = tk.DoubleVar(value=1.0)
        ttk.Label(controls, text="Speed").pack(side='left')
        ttk.Scale(controls, from_=0.1, to=2.0, variable=self.speed, orient='horizontal').pack(side='left')

    def draw_step(self):
        step = self.steps[self.index]
        node = step['node']
        children = step['children']

        G = nx.DiGraph()
        n_name = node.output_signal if hasattr(node, 'output_signal') else str(node)
        G.add_node(n_name)

        for c in children:
            c_name = c.output_signal if hasattr(c, 'output_signal') else str(c)
            G.add_node(c_name)
            G.add_edge(c_name, n_name)

        fig, ax = plt.subplots(figsize=(6, 5))
        pos = nx.spring_layout(G)

        colors = []
        for n in G.nodes():
            if n == n_name:
                colors.append('green' if step['matched'] else 'red')
            else:
                colors.append('skyblue')

        nx.draw(G, pos, with_labels=True, node_color=colors, ax=ax)

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.step_label.config(text=f"Step {self.index + 1} / {len(self.steps)}")

    def next_step(self):
        if self.index < len(self.steps) - 1:
            self.index += 1
            self.draw_step()

    def prev_step(self):
        if self.index > 0:
            self.index -= 1
            self.draw_step()

    def play(self):
        for i in range(self.index, len(self.steps)):
            self.index = i
            self.draw_step()
            self.update()
            time.sleep(max(0.1, 1.5 - self.speed.get()))

# Wrapper to optionally launch GUI after mapping

def tech_mapping_pass(db: TinyDB, lib: TinyLib, visualize=False):
    from utils.PrettyStream import vprint_title, vprint, vprint_pretty, INFO, VERBOSE

    vprint_title("Technology Mapping Pass", v=INFO)
    vprint(f"Mapping {db.name} to technology library {lib.libname}", v=INFO)
    original_db = db
    db = original_db.make_empty_copy()

    for var, node in original_db.vars.items():
        if node is None:
            vprint(f"Skipping input {var}", v=VERBOSE)
            continue
        vprint(f"Mapping {var}...", v=VERBOSE)
        t, _ = tech_map(node, lib, out=var)
        t.state = Node.State.POST_SYNTH
        db.add_var(var, t)
        
    vprint("Mapped", db, v=INFO)
    vprint_pretty(db, v=VERBOSE)

    if visualize:
        app = MappingAnimator(tech_map_steps)
        app.mainloop()

    return db

def match_pattern(node, pattern, env={}):
    #vprint(f"matching \n{node.pretty(PrettyStream())}\n with \n{form.pretty(PrettyStream())}Given:{env}")
    # Check if current node matches the pattern
    if node.cell_name != pattern.cell_name:
        return None
    if len(node.children) != len(pattern.children):
        return None
    # try all permutations to match against gate
    for perm in permutations(node.children):
        # Copy matching environment
        top_env = env.copy() 
        matching_children = 0
        # Match individual Children
        for i in range(len(perm)):
            c = perm[i] # self's child
            f = pattern.children[i] # the patterns's child
            # If child is terminal
            if isinstance(f, str):
                # break if patterns's terminal is already matched to something else
                if f in top_env and c != top_env[f]:
                    matching_children = -1
                    break
                # Match this terminal to patterns's terminal
                top_env[f] = c
                #vprint(f'Matched {f} with {c}',v=PASSED)
                matching_children += 1   
            # If child is node
            elif isinstance(c, Node):
                # try to match the node
                child_env = match_pattern(c,f,top_env)
                if child_env is None: # break if there is no match
                    break 
                else: # otherwise update the env
                    top_env.update(child_env)
                    matching_children += 1
        # If all children matched, we found a match
        if matching_children == len(perm):    
            return top_env
    #vprint("No Match", v=FAILED)
    return None