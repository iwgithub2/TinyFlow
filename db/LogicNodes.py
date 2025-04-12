from db.Node import Node

class NAND(Node):
    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        self.cell_name = "NAND"
        self.input_pins = ["a1","a2"]
        self.output_func = lambda a1, a2: not (a1 and a2)
        self.eval_cell = self.output_func

class AND(Node):
    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        self.cell_name = "AND"
        self.input_pins = ["a1","a2"]
        self.output_func = lambda a1, a2: a1 and a2
        self.eval_cell = self.output_func

class NOR(Node):
    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        self.cell_name = "NOR"
        self.input_pins = ["a1","a2"]
        self.output_func = lambda a1, a2: not (a1 or a2)
        self.eval_cell = self.output_func

class OR(Node):
    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        self.cell_name = "OR"
        self.input_pins = ["a1","a2"]
        self.output_func = lambda a1, a2: a1 or a2
        self.eval_cell = self.output_func

class XOR(Node):
    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        self.cell_name = "XOR"
        self.input_pins = ["a1","a2"]
        self.output_func = lambda a1, a2: a1 ^ a2
        self.eval_cell = self.output_func

class XNOR(Node):
    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        self.cell_name = "XNOR"
        self.input_pins = ["a1","a2"]
        self.output_func = lambda a1, a2: a1 == a2
        self.eval_cell = self.output_func

class INV(Node):
    def __init__(self, a, out=None):
        super(self.__class__, self).__init__([a],out=out)
        self.cell_name = "INV"
        self.input_pins = ["a"]
        self.output_func = lambda a: not a
        self.eval_cell = self.output_func