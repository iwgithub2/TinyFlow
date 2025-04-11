from lark import Lark, Tree, Token
from minisv_exc import IRExtractionPass, ForestryPass, LogicPass, TreeCoveringPass
from minisv_ir import Node
from PrettyStream import vprint, vprint_title, INFO, VERBOSE, DEBUG, ALL
import PrettyStream
import sys
import argparse

def parse(filename, grammar="minisv.lark"):
    with open(filename) as f:
        text = f.read()
    with open(grammar) as f:
        grammar = f.read()
    parser = Lark(grammar, start="start", parser="lalr")
    return parser.parse(text)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Mini System Verilog Parser.")
    parser.add_argument(
        "-g", "--grammar", help="The grammar file to use.", default="minisv.lark"
    )
    parser.add_argument(
        "-o", "--output", help="The output file to write to.", default="output.txt"
    )
    parser.add_argument(
        "-v", "--verbose", help="Increase print verbosity.", action='count', default=0
    )
    parser.add_argument(
        "-p", "--pretty", help="Pretty Print.", action='store_true'
    )
    parser.add_argument(
        "-x", "--extract", help="Extract IR.", action='store_true'
    )
    parser.add_argument(
        "-f", "--forest", help="Generate forests for expressions.", action='store_true'
    )
    parser.add_argument(
        "-t", "--techmap", help="Perform Technology Mapping.", action='store_true'
    )
    parser.add_argument("filename", help="The file to parse.")

    args = parser.parse_args()

    PrettyStream.verbose_level = args.verbose
            
    tree = parse(args.filename, args.grammar)

    modules = {}

    if( args.extract ):
        vprint_title("IR Extraction")
        ext = IRExtractionPass()
        ext.visit_topdown(tree)
        modules = ext.modules
        for name, module in ext.modules.items():
            vprint("Extracted module:", name, "|", module.inputs, "->", module.outputs)
            vprint(module.pretty(),v=VERBOSE)

    if( args.forest ):
        if (not args.extract):
            print("No IR extracted, skipping afforestation.")
            sys.exit(1)
        vprint_title("Foresty Pass")
        for(name, module) in modules.items():
            sub = ForestryPass(module)
            sub.execute()
            modules[name] = sub.module
            vprint("Afforested module:", name)
            vprint(modules[name].pretty(),v=VERBOSE)

    if ( args.techmap ):
        if( (not args.extract)):
            print("No afforestation, skipping Technology Mapping.")
            sys.exit(1)
        vprint_title("Technology Mapping (1/2) - Logic Legalization Pass")
        lg = LogicPass()
        for(name, module) in modules.items():
            for (k, v) in module.vars.items():
                if( v is None and k in module.inputs):
                    vprint(f"Skipping input {k}")
                    continue
                elif( v is None ):
                    vprint(f"Skipping undefined signal {k}")
                    continue
                vprint(f"Legalizing signal {k}...")
                modules[name].vars[k] = lg.transform(v)
                
            vprint(module.pretty(),v=VERBOSE)

        vprint_title("Technology Mapping (2/2) - Tree Covering Pass")
        tc = TreeCoveringPass()
        for(name, module) in modules.items():
            for (k, v) in module.vars.items():
                if( v is None and k in module.inputs):
                    vprint(f"Skipping input {k}")
                    continue
                elif( v is None ):
                    vprint(f"Skipping undefined signal {k}")
                    continue
                
                vprint(f"Mapping signal {k}...")
                vprint(v.pretty(),v=VERBOSE)
                match, cost = tc.match_node(v)
                vprint(k, ">>", match, "cost", cost,v=VERBOSE)

    # aa = TruthTable(["a","b"], 0b0011)
    # bb = TruthTable(["a","b"], 0b1011)
    # cc = TruthTable(["a","b"], 0b0111)

    # ii = TruthTable(["a"], 0b01)

    # tempe = aa @ ["a", "b"]
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(tree.pretty())