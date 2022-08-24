from .base_requirements_relationship import *


class RequirementsVerify(BaseRequirementsRelationship):
    def __init__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)
