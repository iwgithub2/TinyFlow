import json
from utils.PrettyStream import *

class LefCell:
    def __init__(self, name, data):
        self.name = name
        self.cell_class = data.get("class", "CORE")
        self.size = tuple(data.get("size", [0, 0]))
        self.pins = data.get("pins", {})
        self.obs = data.get("obs", [])

    def __repr__(self):
        return f"<LefCell {self.name} size={self.size} pins={list(self.pins.keys())}>"

    def pretty(self, p=None):
        if p is None:
            p = PrettyStream()
        p << [f"Cell {self.name} ({self.cell_class}) size={self.size}"]
        with p:
            for pin, pdata in self.pins.items():
                p << [f"Pin {pin}: dir={pdata['direction']} use={pdata['use']}"]
        return p.cache

class TinyLEF:
    def __init__(self, lef_file="dbfiles/stdcells.lef"):
        self.cells = {}
        self.libname = None
        with open(lef_file, "r") as f:
            data = json.load(f)
            self.libname = data["library"]["name"]
            for cname, cdata in data["cells"].items():
                cell = LefCell(cname, cdata)
                self.cells[cname] = cell

    def __repr__(self):
        return f"LEF library {self.libname} ({len(self.cells)} cells)"

    def pretty(self, p=None):
        if p is None:
            p = PrettyStream()
        p << ["LEF Library", self.libname]
        with p:
            for cell in self.cells.values():
                p << cell.pretty()
        return p.cache