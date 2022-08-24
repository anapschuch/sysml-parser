from .basic import *


class BaseRequirementsRelationship(Basic):
    def __init__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id)
        self.base_directed_relationship = base_directed_relationship
        self.base_abstraction = base_abstraction
