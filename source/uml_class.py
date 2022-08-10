class UMLBasic:
    def __init__(self, name, xmi_id):
        self.name = name
        self.xmi_id = xmi_id
        self.children = []

    def add_children(self, child):
        self.children.append(child)


class UMLPackage(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class UMLClass(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class UMLPort(UMLBasic):
    def __init__(self, name, xmi_id, port_type, aggregation):
        super().__init__(name, xmi_id)
        self.port_type = port_type
        self.aggregation = aggregation


class UMLProperty(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class Basic:
    def __init__(self, xmi_id):
        self.xmi_id = xmi_id
        self.children = []

    def add_children(self, child):
        self.children.append(child)


class Block(Basic):
    def __init__(self, xmi_id, base_class):
        super().__init__(xmi_id)
        self.base_class = base_class


class Model(Basic):
    def __init__(self, xmi_id, name):
        super().__init__(xmi_id)
        self.name = name


class Requirement(Basic):
    def __init__(self, xmi_id, req_id, text, base_named_element, base_class):
        super().__init__(xmi_id)
        self.base_class = base_class
        self.base_named_element = base_named_element
        self.req_id = req_id
        self.text = text
        self.name = None

    def add_name(self, name):
        self.name = name


class BaseRequirementsRelationship(Basic):
    def __init__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id)
        self.base_directed_relationship = base_directed_relationship
        self.base_abstraction = base_abstraction


class RequirementsVerify(BaseRequirementsRelationship):
    def __int__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)


class RequirementsSatisfy(BaseRequirementsRelationship):
    def __int__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)


class RequirementsRefine(BaseRequirementsRelationship):
    def __int__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)

