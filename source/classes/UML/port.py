from .primitive_type import PrimitiveType
from .basic import Basic


class Port(Basic):
    def __init__(self, name, xmi_id, port_type, aggregation):
        super().__init__(name, xmi_id)
        self.port_type = port_type
        self.aggregation = aggregation
        self.direction = None

    def add_direction(self, direction):
        self.direction = direction

    def add_child(self, child):
        if type(child) is PrimitiveType:
            self.port_type = child
        else:
            raise Exception("Unexpected child for UMLPort: ", type(child))

    def print(self, indentation):
        print(' ' * indentation, "Port (", self.direction, "): ", self.xmi_id, " - ", self.name, sep="")
