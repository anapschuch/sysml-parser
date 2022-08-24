from .basic import Basic
from .primitive_type import PrimitiveType
from .default_value import DefaultValue


class Property(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.type = None
        self.defaultValue = None

    def add_children(self, child):
        if type(child) is PrimitiveType:
            self.type = child.type
        elif type(child) is DefaultValue:
            self.defaultValue = child
        else:
            raise Exception("Unexpected child for UMLProperty: ", type(child))

    def print(self, indentation):
        print(' ' * indentation, "Property: ", self.xmi_id, " - ", self.name, sep="")
        if self.defaultValue is not None:
            print(' ' * (indentation + 2), "Default Value: ", self.defaultValue.value_type,
                  " - ", self.defaultValue.value, sep="")
