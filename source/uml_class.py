from .utils import get_primitive_type
from .types import PseudoStateTypes


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
        self.state_machine = None

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
        elif type(child) is UMLStateMachine:
            if self.state_machine is not None:
                raise Exception("Expect at most one state machine in a class")
            self.state_machine = child
        elif type(child) is UMLConstraint:
            super().add_children(child)
        else:
            raise Exception("Unexpected child for UMLClass: ", type(child))


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
        self.specification = None

    def add_children(self, child):
        if type(child) is Specification:
            if self.specification is not None:
                raise Exception("Can only have one specification per Constraint Block")
            self.specification = child


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


class UMLStateMachine(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.regions = []

    def add_children(self, child):
        if type(child) is UMLRegion:
            self.regions.append(child)
        else:
            raise Exception("Unexpected child for UMLStateMachine: ", type(child))


class UMLRegion(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.transitions = dict()
        self.begin_state = None
        self.end_state = None
        self.states = dict()

    def add_children(self, child):
        if type(child) is UMLTransition:
            self.transitions[child.source] = child
        elif type(child) is UMLState:
            self.states[child.xmi_id] = child
        elif type(child) is UMLPseudoState:
            if child.kind == PseudoStateTypes.BEGIN:
                self.begin_state = child
            self.states[child.xmi_id] = child
        elif type(child) is UMLFinalState:
            self.end_state = child
            self.states[child.xmi_id] = child
        else:
            raise Exception("Unexpected child for UMLRegion: ", type(child))


class UMLState(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.state_machine = None
        self.entry = None

    def add_children(self, child):
        if type(child) is UMLStateMachine:
            if self.state_machine is not None:
                raise Exception("Expect at most one state machine in a state")
            self.state_machine = child
        elif type(child) is UMLStateEntryBehavior:
            if self.entry is not None:
                raise Exception("Expect at most one entry behavior in state")
            self.entry = child
        else:
            raise Exception("Unexpected child for UMLState: ", type(child))


class UMLPseudoState(UMLBasic):
    def __init__(self, name, xmi_id, kind):
        super().__init__(name, xmi_id)
        if kind is None:
            self.kind = PseudoStateTypes.BEGIN
        else:
            raise Exception("Unexpected kind for pseudo state:", self.kind)


class UMLFinalState(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)


class UMLTransition:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.trigger = None
        self.constraint = None

    def add_children(self, child):
        if type(child) is UMLTrigger:
            self.trigger = child.event
        elif type(child) is UMLConstraint:
            self.constraint = child.specification
        else:
            raise Exception("Unexpected child for UMLTransition: ", type(child))


class UMLStateEntryBehavior(UMLBasic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.body = None

    def add_children(self, child):
        if type(child) is Body:
            self.body = child.text
        else:
            raise Exception("Unexpected child for UMLStateEntry: ", type(child))


class UMLTrigger:
    def __init__(self, event):
        self.event = event


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


class Specification:
    def __init__(self, xmi_id):
        self.xmi_id = xmi_id
        self.language = "C"
        self.text = None

    def add_children(self, child):
        if type(child) is Body:
            if self.text is not None:
                raise Exception("Can only have one body in a specification tag")
            self.text = child.text
        else:
            raise Exception("Unexpected child for Specification tag")


def print_state_machine(state_machine, indentation):
    for region in state_machine.regions:
        print(' ' * indentation, region.name, ":", region.xmi_id, sep="")
        for state_id, state in region.states.items():
            print(' ' * (indentation + 2), state.name, ":", state_id, sep="")
            if type(state) is UMLState:
                if state.entry is not None:
                    txt = state.entry.body
                    txt = txt.replace('\r\n', '\n' + ' ' * (indentation + 11))
                    print(' ' * (indentation + 4), "entry: ", txt, sep="")
                if state.state_machine is not None:
                    print_state_machine(state.state_machine, indentation + 4)

        if len(region.transitions) > 0:
            print("\n" + ' ' * indentation, "Transitions:", sep="")
            for trans_id, trans in region.transitions.items():
                print(' ' * (indentation + 2), trans.source, "->", trans.target)
                if trans.constraint is not None:
                    print(' ' * (indentation + 4), trans.constraint.text)
