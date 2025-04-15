#==============================================================================
# Tutorial 3: Logging and Printing
#==============================================================================

from db.LogicNodes import AND, INV, OR, XOR

# The PrettyStream module provides both logging and pretty_printing for TinyFlow
from utils import PrettyStream
from utils.PrettyStream import set_verbose_level, vprint, vprint_pretty, PrettyStream

# different verbosity levels, in order of increasing verbosity
from utils.PrettyStream import ERROR, QUIET, WARN, FAILED, PASSED, INFO, VERBOSE, DEBUG, ALL 

node1 = OR(AND(INV("a"),"b"),AND("a",INV("b")))
node2 = XOR("a","b")

# TinyFlow logs information as it executes, and you can control the verbosity level of the logs
# By default the verbosity level is QUIET, so only fatal errors are printed (like the one in tutorial 2)

print("Comparing nodes with QUIET verbosity level:")
assert(node1.logical_eq(node2)) # This will print nothing

print("\nComparing nodes with DEBUG verbosity level:")
# You can change the verbosity level to display more information, including DEBUG prints
set_verbose_level(DEBUG)
assert(node1.logical_eq(node2)) 
# Now for a logical_eq check, you can see what is being compared

# You can use vprint to print information at different verbosity levels
vprint("This is an error message", v=ERROR)
vprint("This is an info message", v=INFO)
vprint("This is a verbose message", v=VERBOSE)
vprint("This is a debug message", v=DEBUG)
vprint("This message has higher verbosity than the current level and shouldn't be printed", v=ALL)

# vprint defaults to INFO verbosity level
vprint("This is a default message")

# Multi-line prints are bracketed for clarity
vprint("Some information 1\nSome information 2", v=INFO)

# We also provide a shortcut for logging pretty printed nodes
vprint_pretty(node1, v=INFO)


# PrettyStream recreates many of the C++ Stream functionality in Python
p = PrettyStream()

# Prints "First" and terminates with a newline
p << "First"

# Prints "Second" and "Third" on the same line, separated by a space
p << ["second","third"]

# Indented printing:
with p: # printing within the block is indented
    p << "Indented by one level"
    with p:
        p << "Indented by two levels"
    p << "Back to one level"
p << "Back to the original level"

# C++ style streaming also works:
p << "Chained1" << "Chained2" << "Chained3"

# Nothing is printed, prints are cached and you can access it with p.cache
print(p.cache)
