from .specification import Specification
from .basic import Basic


class ChangeEvent(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.change_expression = {
            "language": None,
            "body": None,
        }

    def add_children(self, child):
        if type(child) is Specification:
            if self.change_expression["body"] is not None:
                raise Exception("Cannot have two bodies in a change expression")
            self.change_expression["body"] = child.text
            self.change_expression["language"] = child.language
        else:
            raise Exception("Unexpected child for UMLChangeEvent: ", type(child))

    def print(self, indentation):
        if self.change_expression["body"] is not None:
            print(' ' * indentation, self.change_expression["body"])
