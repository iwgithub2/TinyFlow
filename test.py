
from db.TinyDB import TinyDB
from db.TinyLib import TinyLib
from utils.PrettyStream import *
from db.LogicNodes import NAND, INV, AND
from passes.ParserPass import parser_pass
from passes.LogicLegalizePass import logic_legalize_pass
from passes.TechMappingPass import tech_mapping_pass

set_verbose_level(DEBUG)

db = TinyDB("test")

db = parser_pass("verilog/FullAdder.sv")
db_legal = logic_legalize_pass(db)

lib = TinyLib("dbfiles/stdcells.lib")
db_mapped = tech_mapping_pass(db_legal, lib)