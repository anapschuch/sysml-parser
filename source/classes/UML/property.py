from .basic import Basic
from .primitive_type import PrimitiveType
from .default_value import DefaultValue


class Property(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.type = None
        self.default_value = None

    def add_children(self, child):
        if type(child) is PrimitiveType:
            self.type = child.type
        elif type(child) is DefaultValue:
            self.default_value = child.value
        else:
            raise Exception("Unexpected child for UMLProperty: " + type(child))

    def print(self, indentation):
        print(' ' * indentation, f"Property: {self.xmi_id} - {self.name}", sep="")
        if self.default_value is not None:
            print(' ' * (indentation + 2), f"Default Value: {self.default_value}", sep="")
