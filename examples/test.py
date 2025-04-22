from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from utils.PrettyStream import *
from passes.ParserPass import parser_pass
from passes.LogicLegalizePass import logic_legalize_pass
from passes.TechMappingPass import tech_mapping_pass
from utils.Grapher import dump_db_graph

set_verbose_level(DEBUG)

db = parser_pass("verilog/FullAdder.sv")
dump_db_graph(db,"generated/test/db_parsed")

db_legal = logic_legalize_pass(db,False)
dump_db_graph(db_legal,"generated/test/db_legal")
assert(db_legal.logical_eq(db))

lib = TinyLib("dbfiles/stdcells.lib")
db_mapped = tech_mapping_pass(db_legal, lib)
db_mapped.dump_verilog("generated/test/FullAdder_mapped.v")
dump_db_graph(db_mapped,"generated/test/db_mapped")
assert(db_legal.logical_eq(db))