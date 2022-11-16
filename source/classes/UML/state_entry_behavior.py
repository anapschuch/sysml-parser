from .basic import Basic
from .body import Body


class StateEntryBehavior(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.body = None

    def add_child(self, child):
        if type(child) is Body:
            self.body = child.text
        else:
            raise Exception("Unexpected child for UMLStateEntry: ", type(child))
