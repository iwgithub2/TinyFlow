class WireSegment:
    def __init__(self, layer, start_point, end_point, width):
        self.layer = layer
        self.start_point = start_point
        self.end_point = end_point
        self.width = width
    
    def __repr__(self):
        return f"Wire(layer={self.layer}, from={self.start_point} to={self.end_point})"

class Via:
    def __init__(self, location, from_layer, to_layer):
        self.location = location
        self.from_layer = from_layer
        self.to_layer =to_layer
    
    def __repr__(self):
        return f"Via(at={self.location}, from={self.from_layer} to={self.to_layer})"

class Net:
    def __init__(self, name):
        self.name = name 
        self.wire_segments = []
        self.vias = []

    def add_wire_segment(self, layer, start_point, end_point, width):
        """Helper method to add a wire segment to the net."""
        segment = WireSegment(layer, start_point, end_point, width)
        self.wire_segments.append(segment)

    def add_via(self, location, from_layer, to_layer):
        """Helper method to add a via to the net."""
        via = Via(location, from_layer, to_layer)
        self.vias.append(via)
    
    def __repr__(self):
        return f"Net(name='{self.name}', wires={len(self.wire_segments)}, vias={len(self.vias)})"