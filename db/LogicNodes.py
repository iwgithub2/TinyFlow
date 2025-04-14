from db.Node import Node

class NAND(Node):
    cell_name = "NAND"
    input_pins = ["a1","a2"]
    output_func = lambda a1, a2: not (a1 and a2)

    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)

class AND(Node):
    cell_name = "AND"
    input_pins = ["a1","a2"]
    output_func = lambda a1, a2: a1 and a2

    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        
class NOR(Node):
    cell_name = "NOR"
    input_pins = ["a1","a2"]
    output_func = lambda a1, a2: not (a1 or a2)

    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)
        

class OR(Node):
    cell_name = "OR"
    input_pins = ["a1","a2"]
    output_func = lambda a1, a2: a1 or a2

    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)


class XOR(Node):
    cell_name = "XOR"
    input_pins = ["a1","a2"]
    output_func = lambda a1, a2: a1 ^ a2

    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)

class XNOR(Node):
    cell_name = "XNOR"
    input_pins = ["a1","a2"]
    output_func = lambda a1, a2: a1 == a2

    def __init__(self, a1, a2, out=None):
        super(self.__class__, self).__init__([a1,a2],out=out)

class INV(Node):
    cell_name = "INV"
    input_pins = ["a"]
    output_func = lambda a: not a

    def __init__(self, a, out=None):
        super(self.__class__, self).__init__([a],out=out)