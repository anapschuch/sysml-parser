from .basic import Basic
from .connector_end import ConnectorEnd


class Connector(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.ends = []

    def add_children(self, child):
        if type(child) is not ConnectorEnd:
            raise Exception("Unexpected child for UMLConnector: ", type(child))
        else:
            self.ends.append(child.role)
