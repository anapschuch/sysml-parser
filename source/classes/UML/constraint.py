from .basic import Basic
from .specification import Specification


class Constraint(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.specification = None

    def add_children(self, child):
        if type(child) is Specification:
            if self.specification is not None:
                raise Exception("Can only have one specification per Constraint Block")
            self.specification = child.text
