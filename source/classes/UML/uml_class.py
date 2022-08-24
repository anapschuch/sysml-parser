from .basic import *
from .port import Port
from .property import Property
from .connector import Connector
from .state_machine import StateMachine
from .constraint import Constraint


class Class(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.attributes = dict()
        self.attribute_names = dict()
        self.children_attributes = dict()
        self.connectors = dict()
        self.state_machine = None
        self.constraints = []

    def add_children(self, child):
        if type(child) is Port or type(child) is Property:
            self.attributes[child.xmi_id] = child
            self.attribute_names[child.name] = child.xmi_id
        elif type(child) is Connector:
            if len(child.ends) != 2:
                raise Exception("Found a connector without two ends: ", child.xmi_id)
            self.connectors[child.ends[0]] = child.ends[1]
            self.connectors[child.ends[1]] = child.ends[0]
        elif type(child) is Class:
            for attr_id, _ in child.attributes.items():
                self.children_attributes[attr_id] = child
            super().add_children(child)
        elif type(child) is StateMachine:
            if self.state_machine is not None:
                raise Exception("Expect at most one state machine in a class")
            self.state_machine = child
        elif type(child) is Constraint:
            self.constraints.append(child)
        else:
            raise Exception("Unexpected child for UMLClass: ", type(child))
