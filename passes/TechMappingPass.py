from multiprocessing import reduction
from utils.PrettyStream import *
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from db.Node import Node
from db.LogicNodes import *
from itertools import permutations
import math
from copy import deepcopy

def tech_mapping_pass(db: TinyDB, lib:TinyLib):
    vprint_title("Technology Mapping Pass", v=INFO)
    vprint(f"Mapping {db.name} to technology library {lib.libname}", v=INFO)
    original_db = db
    db = deepcopy(db)
    for var, node in db.vars.items():
        if node is None:
            vprint(f"Skipping input {var}", v=VERBOSE)
            continue
        vprint(f"Mapping {var}...", v=VERBOSE)
        t, _ = tech_map(node, lib)
        t.state = Node.State.POST_SYNTH
        db.vars[var] = t
    vprint("Mapped", db, v=INFO)
    vprint_pretty(db, v=VERBOSE)
    vprint(f"Validating mapped database against original...", v=INFO)
    db.logical_eq(original_db)
    return db

def tech_map(node: Node, lib: TinyLib, top_node=True):
    if node.optimal_match is not None:
        return node.optimal_match
    
    best_cost = math.inf
    best_tree = None
    
    for cell_name, cell in lib.cells.items():
        for form in cell.tree_forms:
            cost = lib.cell_costs[cell_name]
            result = match_form(node, form)
            if result is None:
                continue
            for port, wire in result.items():
                if isinstance(wire,Node):
                    m, c = tech_map(wire, lib, top_node=False)
                    cost += c
                    result[port] = m
            children = [result[pin] for pin in cell.input_pins]
            tree = cell(*children)
            vprint(f"Found mapping for {node.output_signal} with cost {cost}: {tree}", v=DEBUG if top_node else ALL)
            if cost < best_cost:
                best_tree = tree
                best_cost = cost

    node.optimal_match = best_tree, best_cost
    return best_tree, best_cost

def match_form(node, form, env={}):
    #vprint(f"matching \n{node.pretty(PrettyStream())}\n with \n{form.pretty(PrettyStream())}Given:{env}")
    # Check if current node matches the form
    if node.cell_name != form.cell_name:
        return None
    if len(node.children) != len(form.children):
        return None
    # try all permutations to match against gate
    for perm in permutations(node.children):
        # Copy matching environment
        top_env = env.copy() 
        matching_children = 0
        # Match individual Children
        for i in range(len(perm)):
            c = perm[i] # self's child
            f = form.children[i] # the form's child
            # If child is terminal
            if isinstance(f, str):
                # break if form's terminal is already matched to something else
                if f in top_env and c != top_env[f]:
                    matching_children = -1
                    break
                # Match this terminal to form's terminal
                top_env[f] = c
                #vprint(f'Matched {f} with {c}',v=PASSED)
                matching_children += 1   
            # If child is node
            elif isinstance(c, Node):
                # try to match the node
                child_env = match_form(c,f,top_env)
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