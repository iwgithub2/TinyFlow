from enum import Enum

class IOPort:
    """
    Represents a single I/O pad in teh circuit
    This is a physical obkect that can be placed on the boundary of the design
    """

    class Direction(Enum):
        INPUT = 0
        OUTPUT = 1
        INOUT = 2
    
    def __init__(self, name, direction):
        if not isinstance(direction, self.Direction):
            raise TypeError("Port direction must be an IO")

        self.name = name
        self.direction = direction
        self.placement = None
    
    def set_placement(self, x, y):
        self.placement = (x,y)
    
    def is_placeed(self):
        return self.placement is not None
    
    def __repr__(self):
        return f"IOPort(name='{self.name}', direction={self.direction.name})"