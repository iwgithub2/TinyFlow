#==============================================================================
# Tutorial 5: TinyLib files
#==============================================================================

# Frontend EDA tools typically accept a library file, which contains
# - Technology information
# - List of available standard cells
# - Logic and timing information for each cell

# TinyFlow also provides a minimal library file format - TinyLib

# A TinyLib files is a json with the following structure:
#
# - "library"
#   - "name": str
#   - "version": str
#   - "description": str
# - "cells"
#   - cell_name
#     - "pins"
#       - pin_name: "input" | lambda
#       ...
#     - "dimen": [number, number]
#     - "cost": number
#     - "patterns": [str, ...]
#   ...
#
# An example TinyLib file is provided in dbfiles/stdcells.lib

# !! Note that TinyLib currently only supports single-output cells. !!
# So only one pin can have a lambda expression, and it must be the output pin.

# You can load a TinyLib file using the TinyLib class
from db.TinyLib import TinyLib
from utils.PrettyStream import set_verbose_level, vprint_pretty, INFO, vprint

lib = TinyLib("dbfiles/stdcells.lib")
set_verbose_level(INFO)
vprint("Loaded library:", v=INFO)
vprint_pretty(lib)

# TinyLib's constructor will automatically generated subclasses for each cell
# and load them into the global namespace.

# Let's try to spawn an instance of a generated class:
try:
    nor_cell = NOR2D1("a","b")
except NameError:
    vprint("Caught an exception!")
    vprint("NOR2D1 is not yet imported, we need to import it after constructing the TinyLib object")

# To access them outside of the TinyLib module, you need to import them *after* constructing the TinyLib object. 
from db.TinyLib import *
# !! This import will not work if you put it before the TinyLib constructor !!

# And now you can spawn and use instances of the generated classes just like the built-in LogicNodes:
nor_cell = NOR2D1("a","b")
nor_logic = NOR("a","b")
assert(nor_logic.logical_eq(nor_cell))

# The TinyLib constructor also sets several static attributes for generated classes, including:
# - cell_name: the name of the stdcell
# - input_pins: list of input pins
# - output_pin: the output pin
# - output_func: the output function
# - patterns: list of patterns to use for tech mapping
#
# These attributes are fixed for the class and cannot be changed.
# You can access these attributes using the class name or the class object.
p = PrettyStream()
p << "NOR2D1 has the following patterns: "
with p:
    for pattern in NOR2D1.patterns:
        p << pattern
vprint(p.cache)