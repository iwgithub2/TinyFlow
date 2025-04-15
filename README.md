# TinyFlow
A tiny EDA toolflow built-in python for RTL-GDS compilation, currently supporting a small subset of SystemVerilog.
TinyFlow includes a TinyDB, TinyLib, and 3 frontend passes. Development is in progress to implement the backend passes with lambda-rule based standard cells.

## Installing TinyFlow
Requirements: Python >= 3.11.9
```
python -m venv venv/
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Started
The frontend of TinyFlow consists three different class:
- TinyDB (Represents a module as a collection of logic trees)
- Node (Represents a node in a logic tree)
- TinyLib (Collection of standard cell informations)

### Build Logic Trees in TinyFlow
First, try out building a logic tree in TinyFlow, TinyFlow provides a set of standard logic nodes in `db.LogicNodes`: 
- `INV`, `AND`, `NAND`, `OR`, `NOR`, `XOR`, `XNOR`

Instantiating a NAND gate with inputs a and b is as simple as `NAND("a","b")`, you can also created nested trees:
```
AND(INV("a"),OR("b","c"))
```

### Supported Verilog Syntax
- All ports/variables must be of single-bit `logic` datatype, arrays (both packed and unpacked are not supported).
- Monolithic modules without parameters, hierarchy(instantiating modules) is not supported.
- Local variable declarations
- Assign statements
- Six operators: `~`, `&`, `~&`, `|`, `~|`, `^`, `~^`
- Nested Unary/Binary Expressions (without precendence support, must explicitly declare precedence with parenthesis
  - E.g. `a & (b & c)` is supported, but not `a & b & c`, similarly `(~a) | b` is supported but not `~a | b`.
- Example Supported Verilog: [FullAdder](https://github.com/fangzhonglyu/TinyFlow/blob/fbc21083a1282564b84b1a2b1780d2c8abd4efcf/verilog/FullAdder.sv#L1-L12)
