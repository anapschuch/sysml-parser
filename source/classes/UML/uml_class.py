from enum import Enum
from .basic import *
from .port import Port
from .property import Property
from .connector import Connector
from .state_machine import StateMachine
from .constraint import Constraint


class ClassType(Enum):
    CONSTRAINT_BLOCK = 'CONSTRAINT_BLOCK'
    BLOCK = 'BLOCK'


class Class(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.attributes = dict()
        self.attribute_names = dict()
        self.children_attributes = dict()
        self.connectors = dict()
        self.state_machine = None
        self.constraints = []
        self.type = None

    def add_children(self, child):
        if type(child) is Port or type(child) is Property:
            self.attributes[child.xmi_id] = child
            self.attribute_names[child.name] = child.xmi_id
        elif type(child) is Connector:
            if len(child.ends) != 2:
                raise Exception("Found a connector without two ends: " + child.xmi_id)

            if child.ends[0] not in self.connectors:
                self.connectors[child.ends[0]] = [child.ends[1]]
            else:
                self.connectors[child.ends[0]].append(child.ends[1])

            if child.ends[1] not in self.connectors:
                self.connectors[child.ends[1]] = [child.ends[0]]
            else:
                self.connectors[child.ends[1]].append(child.ends[0])
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
            raise Exception("Unexpected child for UMLClass: " + type(child))

    def set_type(self, class_type):
        if self.type is not None:
            raise Exception("Unable to set type in class because it has already set before. Class name: " + self.name)
        else:
            self.type = class_type

    def get_type(self):
        return self.type

    def __str__(self):
        if self.type == ClassType.CONSTRAINT_BLOCK:
            return f'Constraint Block: \'{self.name}\''
        if self.type == ClassType.BLOCK:
            return f'Block: \'{self.name}\''

        raise Exception(f"Unexpected class type: '{self.type}'")
