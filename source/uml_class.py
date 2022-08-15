from .utils import get_primitive_type


class UMLBasic:
    def __init__(self, name, xmi_id):
        self.name = name
        self.xmi_id = xmi_id
        self.children = dict()

    def add_children(self, child):
        if child is None:
            raise Exception("Error: trying to add a None child")
        self.children[child.xmi_id] = child


class UMLModel(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class UMLPackage(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class UMLClass(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.attributes = dict()
        self.attribute_names = dict()
        self.children_attributes = dict()
        self.connectors = dict()

    def add_children(self, child):
        if type(child) is UMLPort or type(child) is UMLProperty:
            self.attributes[child.xmi_id] = child
            self.attribute_names[child.name] = child.xmi_id
        elif type(child) is UMLConnector:
            if len(child.ends) != 2:
                raise Exception("Found a connector without two ends: ", child.xmi_id)
            self.connectors[child.ends[0]] = child.ends[1]
            self.connectors[child.ends[1]] = child.ends[0]
        elif type(child) is UMLClass:
            for attr_id, _ in child.attributes.items():
                self.children_attributes[attr_id] = child
            super().add_children(child)
        else:
            super().add_children(child)


class UMLConnector(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.ends = []

    def add_children(self, child):
        if type(child) is UMLConnectorEnd:
            self.ends.append(child.role)
        else:
            raise Exception("Unexpected child for UMLConnector: ", type(child))


class UMLConnectorEnd:
    def __init__(self, role):
        self.role = role


class UMLPort(UMLBasic):
    def __init__(self, name, xmi_id, port_type, aggregation):
        super().__init__(name, xmi_id)
        self.port_type = port_type
        self.aggregation = aggregation
        self.direction = None

    def add_direction(self, direction):
        self.direction = direction

    def add_children(self, child):
        if type(child) is UMLPrimitiveType:
            self.port_type = child
        else:
            raise Exception("Unexpected child for UMLPort: ", type(child))


class UMLConstraint(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class UMLProperty(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.type = None
        self.defaultValue = None

    def add_children(self, child):
        if type(child) is UMLPrimitiveType:
            self.type = child.type
        elif type(child) is DefaultValue:
            self.defaultValue = child
        else:
            raise Exception("Unexpected child for UMLProperty: ", type(child))


class UMLPrimitiveType:
    def __init__(self, href):
        self.type = get_primitive_type(href)


class DefaultValue:
    def __init__(self, value_type, xmi_id):
        self.xmi_id = xmi_id
        self.value_type = value_type
        if value_type == "uml:LiteralReal":
            self.body = 0.0
        else:
            self.body = None

    def add_children(self, child):
        self.body = child


class Basic:
    def __init__(self, xmi_id):
        self.xmi_id = xmi_id


class Block(Basic):
    def __init__(self, xmi_id, base_class):
        super().__init__(xmi_id)
        self.base_class = base_class


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
    def __init__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)


class RequirementsSatisfy(BaseRequirementsRelationship):
    def __init__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)


class RequirementsRefine(BaseRequirementsRelationship):
    def __init__(self, xmi_id, base_directed_relationship, base_abstraction):
        super().__init__(xmi_id, base_directed_relationship, base_abstraction)


class Body:
    def __init__(self, text):
        self.text = text



