from lark import Lark

with open("verilog.lark") as f:
    grammar = f.read()
parser = Lark(grammar, start="start", parser="lalr", lexer="contextual")

with open("Mult.v") as f:
    text = f.read()

tree = parser.parse(text)
print(tree.pretty())