#==============================================================================
# Tutorial 5: TinyFlow Parsing
#==============================================================================

# Parsing in TinyFlow is based on the Python Lark package.
# Lark is a powerful parsing library that can be used to parse any context-free grammar.

# To parse a text file in with Lark, you have to define an EBNF grammar.
# EBNF specifies the production rules for the grammar, which are used to parse the input text.

# The grammar is defined in a string, which is passed to the Lark constructor.

import ast
from lark import Lark, v_args

from utils.PrettyStream import set_verbose_level, vprint, INFO

set_verbose_level(INFO)

# Define a simple grammar that parses a color:
# This grammar specifies a threes rule
#  - object: which accepts a color and a SHAPE with a space in between
#  - color: which accepts either "red", "green" or "blue"  
#  - SHAPE: which accepts either "circle", "square" or "triangle"
g1 = """
    object: color " " SHAPE 
    color: "red" | "green" | "blue"
    SHAPE: "circle" | "square" | "triangle"
    """

# Create a parser using the grammar, and tell it that it should use the "object" rule as the start rule.
# Notice that we use the LALR parser:
# It is a determinstic parser that only accepts deterministic grammars (Only one possible syntax tree for each input).
parser1 = Lark(g1, start="object", parser="lalr")

# Let's try to parse some valid text:
ast1_1 = parser1.parse("green circle")
print("Parsed ast1_1:", ast1_1)
print("Pretty Printing ast1_1:\n",ast1_1.pretty())
# We can see that the parser accepted the input text and generated an abstract syntax tree(AST) in this structure:
#
#               Token('RULE', 'object')
#              /                      \
#    Token('RULE, 'color')      Token('SHAPE', 'circle')
#
# Notice that the space is not recorded in the AST, since it is a literal.
# Similarly the actual color is not recorded in the AST, becuase they are also literals.

# To record the value of the literal, you have to specify a terminal rule with an all caps name.
# For example, the value of SHAPE is recorded in the AST

# Let's try to parse some invalid text:
try:
    ast1_2 = parser1.parse("yellow")
except Exception as e:
    vprint("Caught an exception:", e)
# Notice that this fails and throughs an exception, rejecting the input text.

# Let's try to make a slightly more complex grammar:
# The following grammar parses a greeting:
# - It accepts either "hello" or "hi" as the greeting
# - It accepts a name, which is a sequence of letters of any positive length, speecified by a regex
# - It accepts 0 or more "very" before "nice"
# - It ignores whitespace and commas, so rules don't need to specify them explicitly
g2 = """
    greeting: ("hello" | "hi") NAME "it's" "a" "very"* "nice" "day"
    NAME: /[a-zA-Z]+/

    %import common.WS
    %ignore WS
    %ignore ","
    """

# If you aren't familar with BNF grammar, check out the lark grammar docs at: 
# https://lark-parser.readthedocs.io/en/stable/grammar.html

# Parsing some valid text:
parser2 = Lark(g2, start="greeting", parser="lalr")
ast2_1 = parser2.parse("hi Barry, it's a nice day")
print("Parsed ast2_1:", ast2_1)
print("Pretty Printing ast2_1:\n",ast2_1.pretty())


ast2_2 = parser2.parse("hello Vayun, it's a very very nice day")
print("Parsed ast2_2:", ast2_2)
print("Pretty Printing ast2_2:\n",ast2_2.pretty())

# Check out the Lark documentation for more information on how to use Lark:
# https://lark-parser.readthedocs.io/en/stable/index.html

# You can traverse the AST in many ways, either with Lark APIs or by directly traversing the tree.
# For example, you can use the Lark visitor to traverse and transform the tree in a bottome up fashion.
from lark.visitors import Transformer

class GreetingTraverser(Transformer):
    @v_args(tree=True)
    def greeting(self, tree):
        print("Visiting greeting:", tree)
        return tree.children[0]

    @v_args(tree=True)
    def NAME(self, tree):
        print("Visiting NAME:", tree)
        return tree
    
traverser = GreetingTraverser()
print("Transforming ast2_1:", )
transformed = traverser.transform(ast2_1)
print("We've extracted the name after transformation:")
print(transformed)
