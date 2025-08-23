from algorithms.bfs import bfs_router
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib

def simple_router(db : TinyDB, lib : TinyLib):
    print("Running a simple router")

    # Create the coordinates dictionary
    for gate, ports, uid in db.get_netlist():
        

    # nets = bfs_router(coordinates_dict, connection_list, grid_dimen, layers=1)

    # visualize_routing(
    #     db=db,
    #     layers=['M1', 'M2', 'M3', 'M4'] # Ensure this matches the layers used in routing
    # )
