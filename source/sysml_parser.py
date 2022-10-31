from xml.etree import ElementTree

from .classes import *
from source.xml_types import *
from .validators import validate_element
from .utils import is_tag_requirement_type, raise_error


class SysMLParser:
    def __init__(self, filename):
        self.filename = filename
        self.namespaces = self.get_namespaces()
        self.tag_types = self.get_tag_types_from_path(XMLTagTypes)
        self.tag_attributes = self.get_tag_types_from_path(XMLTagAttributeTypes)
        self.tag_attributes_types_path = self.get_tag_path_from_type(XMLTagAttributeTypes)
        self.tag_xmi_types = {i.value: i for i in XMITypeTypes}
        self.root = ElementTree.parse(filename).getroot()
        self.ids = dict()
        self.base_ids = dict()
        self.items_flow = dict()
        self.items_flow_reversed = dict()
        self.blocks = []
        self.triggers = dict()

    def get_tag_types_from_path(self, types_list):
        tag_types = dict()
        for tag_type in list(types_list):
            path = self.get_tag_path(tag_type.value)
            tag_types[path] = tag_type
        return tag_types

    def get_tag_path_from_type(self, types_list):
        tag_paths = dict()
        for tag_type in list(types_list):
            path = self.get_tag_path(tag_type.value)
            tag_paths[tag_type] = path
        return tag_paths

    def get_namespaces(self):
        return dict([
            elem for _, elem in ElementTree.iterparse(self.filename, events=['start-ns'])
        ])

    def get_tag_path(self, tag):
        path = tag.split(":")
        full_tag = ""
        for idx in range(len(path) - 1):
            full_tag += "{" + self.namespaces.get(path[idx], '') + "}"
        full_tag += path[len(path) - 1]
        return full_tag

    def get_tag_type(self, tag):
        if tag not in self.tag_types:
            raise Exception("XML Tag '" + tag + "' not defined")
        return self.tag_types.get(tag)

    def get_tag_attribute_type(self, attrib):
        if attrib not in self.tag_attributes:
            raise Exception("XML Tag Attribute '" + attrib + "' not defined")
        return self.tag_attributes.get(attrib)

    def get_tag_xmi_type(self, xmi_type):
        if xmi_type not in self.tag_xmi_types:
            raise Exception("XML Tag Attribute xmi:type '" + xmi_type + "' not defined")
        return self.tag_xmi_types.get(xmi_type)

    def get_tag_attr(self, attr, attr_type):
        return attr.get(self.tag_attributes_types_path[attr_type], None)

    def parse_tag(self, tag, parent):
        xmi_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.XMI_ID)
        tag_type = self.get_tag_type(tag.tag)
        element = None

        if tag_type == XMLTagTypes.MODEL:
            element = Model(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

        elif tag_type == XMLTagTypes.BLOCK or tag_type == XMLTagTypes.CONSTRAINT_BLOCK:
            base_class = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_CLASS)
            base_class_elem = self.ids[base_class]
            if type(base_class_elem) is not Class:
                raise Exception("Unexpected type for base class in element " + xmi_id)
            if tag_type == XMLTagTypes.BLOCK:
                base_class_elem.set_type(ClassType.BLOCK)
                self.blocks.append(base_class_elem)
            else:
                base_class_elem.set_type(ClassType.CONSTRAINT_BLOCK)

        elif tag_type == XMLTagTypes.BODY:
            element = Body(tag.text)

        elif tag_type == XMLTagTypes.SPECIFICATION or tag_type == XMLTagTypes.CHANGE_EXPRESSION:
            element = Specification(xmi_id)

        elif tag_type == XMLTagTypes.DEFAULT_VALUE:
            element = DefaultValue(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.XMI_TYPE),
                                   self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.VALUE), xmi_id)

        elif tag_type == XMLTagTypes.ENTRY:
            element = StateEntryBehavior(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

        elif tag_type == XMLTagTypes.FLOW_PORT:
            base_port_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_PORT)
            base_port = self.ids.get(base_port_id, None)
            if base_port is None:
                raise Exception("Base Port id " + base_port_id + " not found")
            if type(base_port) is not Port:
                raise Exception("Unexpected base port type: " + type(base_port))
            direction = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.DIRECTION)
            if direction is None:
                parent = self.ids.get(base_port.parent, None)
                location_error = f'\nLocation:\n{parent}'
                raise_error("Missing direction for flow port '" + base_port.name +
                            "' (direction inout not allowed)" + location_error)
            base_port.add_direction(direction)

        elif is_tag_requirement_type(tag_type):
            if tag_type == XMLTagTypes.REQUIREMENT:
                req_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.ID)
                text = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.TEXT)
                base_named_element = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_NAMED_ELEMENT)
                base_class = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_CLASS)
                element = Requirement(xmi_id, req_id, text, base_named_element, base_class)

                self.base_ids[base_class] = element

            base_directed_relationship = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_DIRECTED_RELATIONSHIP)
            base_abstraction = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_ABSTRACTION)

            if tag_type == XMLTagTypes.REQUIREMENTS_REFINE:
                element = RequirementsRefine(xmi_id, base_directed_relationship, base_abstraction)

            elif tag_type == XMLTagTypes.REQUIREMENTS_VERIFY:
                element = RequirementsVerify(xmi_id, base_directed_relationship, base_abstraction)

            elif tag_type == XMLTagTypes.REQUIREMENTS_SATISFY:
                element = RequirementsSatisfy(xmi_id, base_directed_relationship, base_abstraction)

            self.base_ids[base_abstraction] = element

        else:
            xmi_type_string = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.XMI_TYPE)
            if xmi_type_string is not None:
                xmi_type = self.get_tag_xmi_type(xmi_type_string)

                if xmi_type == XMITypeTypes.PACKAGE:
                    element = Package(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.CLASS:
                    element = Class(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PORT:
                    element = Port(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id, None,
                                   self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.AGGREGATION))

                elif xmi_type == XMITypeTypes.CONSTRAINT:
                    element = Constraint(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PROPERTY:
                    element = Property(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PRIMITIVE_TYPE:
                    element = PrimitiveType(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.HREF))

                elif xmi_type == XMITypeTypes.CONNECTOR:
                    element = Connector(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.CONNECTOR_END:
                    element = ConnectorEnd(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.ROLE))

                elif xmi_type == XMITypeTypes.INFORMATION_FLOW:
                    source = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.INFORMATION_SOURCE).split(' ')
                    target = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.INFORMATION_TARGET).split(' ')
                    source_string = source[len(source)-1]
                    target_string = target[len(target)-1]
                    element = InformationFlow(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id,
                                              source_string, target_string)

                    source_element = self.ids.get(source_string)
                    target_element = self.ids.get(target_string)

                    st = {source_element: 'source', target_element: 'target'}
                    for k, v in st.items():
                        if type(k) != Port and type(k) != Property:
                            raise_error(f'Item flow {v} is not a Port or a Property\nSource: \'{source_element.name}\''
                                        f'\nTarget: \'{target_element.name}\'\nItemFlow id: \'{xmi_id}\'')

                    if source_string in self.items_flow:
                        self.items_flow[source_string].append(target_string)
                    else:
                        self.items_flow[source_string] = [target_string]

                    if target_string in self.items_flow_reversed:
                        self.items_flow_reversed[target_string].append(source_string)
                    else:
                        self.items_flow_reversed[target_string] = [source_string]

                elif xmi_type == XMITypeTypes.STATE_MACHINE:
                    element = StateMachine(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.REGION:
                    element = Region(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.STATE:
                    element = State(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PSEUDO_STATE:
                    element = PseudoState(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id,
                                          self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.KIND))

                elif xmi_type == XMITypeTypes.FINAL_STATE:
                    element = FinalState(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.TRANSITION:
                    element = Transition(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.SOURCE),
                                         self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.TARGET))

                elif xmi_type == XMITypeTypes.TRIGGER:
                    event_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.EVENT)
                    element = Trigger(xmi_id, event_id)
                    aux = self.triggers.get(event_id, None)
                    if aux is None:
                        self.triggers[event_id] = [element]
                    else:
                        self.triggers[event_id].append(element)

                elif xmi_type == XMITypeTypes.CHANGE_EVENT:
                    element = ChangeEvent(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)
                    for trigger in self.triggers[xmi_id]:
                        trigger.event = element

        self.ids[xmi_id] = element
        if element is not None:
            for child in tag:
                parsed_child = self.parse_tag(child, element)
                if parsed_child is not None:
                    element.add_children(parsed_child)
                    if hasattr(element, 'xmi_id'):
                        parsed_child.parent = element.xmi_id

        validate_element(element, parent)
        return element
