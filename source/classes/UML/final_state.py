from .basic import Basic


class FinalState(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)

    def print(self, indentation):
        print(' ' * indentation, self.name, ": ", self.xmi_id, sep="")
