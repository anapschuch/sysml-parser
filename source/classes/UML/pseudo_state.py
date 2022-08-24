from .basic import Basic
from ...types import PseudoStateTypes


class PseudoState(Basic):
    def __init__(self, name, xmi_id, kind):
        super().__init__(name, xmi_id)
        if kind is None:
            self.kind = PseudoStateTypes.BEGIN
        else:
            raise Exception("Unexpected kind for pseudo state:", self.kind)

    def print(self, indentation):
        print(' ' * indentation, self.name, ": ", self.xmi_id, sep="")
