from lark import Lark
from pre_synth_ir import *
from pre_synth_opt import *

with open("sv2012.lark") as f:
    grammar = f.read()
parser = Lark(grammar, start="start", parser="lalr")

with open("Simple.sv") as f:
    text = f.read()


tree = parser.parse(text)
print(tree)

tree = ExprSubstitutePass().transform(tree)

irexc = IRExtractionPass()

tree = irexc.visit(tree)

print(tree)

modules = irexc.modules

for module in modules.values():
    constantFoldModule(module, tree)
    # print(module)

# print(tree)

# for module in irexc.modules.values():
#     print(module)