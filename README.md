# TinyFlow
A tiny EDA toolflow built in python for RTL-GDS compilation, currently supporting a small subset of SystemVerilog.
TinyFlow includes a TinyDB, TinyLib, and 3 frontend passes. Development is in progress to implement the backend passes with lambda-rule based standard cells.

## Installing TinyFlow
Requirements: Python >= 3.11.9

Create a virtual environment if needed
```
python -m venv venv/ 
source venv/bin/activate
```

Install required python packages with pip
```
pip install -r requirements.txt
```

## Getting Started
The frontend of TinyFlow consists three different class:
- TinyDB (Represents a module as a collection of logic trees)
- Node (Represents a node in a logic tree)
- TinyLib (Collection of standard cell informations)

---

### Running Tutorials/Examples
Checkout code tutorials and examples in [examples](examples)

To run tutorial 1, run `python -m examples.tutorial_1` from the TinyFlow root directory

---

### Build Logic Trees in TinyFlow 
First, try out building a logic tree in TinyFlow, TinyFlow provides a set of standard logic nodes in `db.LogicNodes`: 
- `INV`, `AND`, `NAND`, `OR`, `NOR`, `XOR`, `XNOR`

Instantiating a NAND gate with inputs a and b is as simple as `NAND("a","b")`, you can also created nested trees:
```
node1 = AND(INV("a"),OR("b","c"))
```

You can visualize the node as well by calling:
```
dump_node_graph(node1, "generated/tut_1/node1", label="Tree Visualization")
```
![tut1_node1](https://github.com/user-attachments/assets/479c35c6-faf3-43a4-9b21-57cf5e3be9ee)

(More in [Tutorial 1](examples/tutorial_1.py))

---

### Evaluating Logic Trees 
Logic Trees can be evaluated with the `eval()` method:
```
node1.eval(a=0,b=0,c=0) # returns 0
node1.eval({'a'=0,'b'=1,'c'=0}) # Alternatively feed in a dict (returns 1)
```
Logic Trees can be checked logically equivalence with the `logical_eq()` method:
```
nand = NAND('a','b')
not_and = INV(AND('a','b'))
nand.logical_eq(not_and) # returns True
```
(More in [Tutorial 2](examples/tutorial_2.py))

---

## Supported Verilog Syntax
- All ports/variables must be of single-bit `logic` datatype, arrays (both packed and unpacked are not supported).
- Monolithic modules without parameters, hierarchy(instantiating modules) is not supported.
- Local variable declarations
- Assign statements
- Six operators: `~`, `&`, `~&`, `|`, `~|`, `^`, `~^`
- Nested Unary/Binary Expressions (without precendence support, must explicitly declare precedence with parenthesis
  - E.g. `a & (b & c)` is supported, but not `a & b & c`, similarly `(~a) | b` is supported but not `~a | b`.
- Example Supported Verilog: [FullAdder](verilog/FullAdder.sv)
