import xml.etree.ElementTree as ElementTree
from source import *
from xml_types import *


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
            full_tag += "{" + self.namespaces.get(path[idx]) + "}"
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

    def parse_tag(self, tag):
        xmi_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.XMI_ID)
        tag_type = self.get_tag_type(tag.tag)
        element = None

        if tag_type == XMLTagTypes.MODEL:
            element = UMLModel(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

        elif tag_type == XMLTagTypes.BLOCK:
            base_class = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_CLASS)
            element = Block(xmi_id, base_class)
            self.blocks.append(element)

        elif tag_type == XMLTagTypes.BODY:
            element = Body(tag.text)

        elif tag_type == XMLTagTypes.SPECIFICATION or tag_type == XMLTagTypes.CHANGE_EXPRESSION:
            element = Specification(xmi_id)

        elif tag_type == XMLTagTypes.DEFAULT_VALUE:
            element = DefaultValue(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.XMI_TYPE), xmi_id)

        elif tag_type == XMLTagTypes.ENTRY:
            element = UMLStateEntryBehavior(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

        elif tag_type == XMLTagTypes.FLOW_PORT:
            base_port_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.BASE_PORT)
            base_port = self.ids.get(base_port_id, None)
            if base_port is None:
                raise Exception("Base Port id ", base_port_id, " not found")
            if type(base_port) is not UMLPort:
                raise Exception("Unexpected base port type: ", type(base_port))
            direction = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.DIRECTION)
            if direction is None:
                raise Exception("Missing direction for flow port ", base_port_id)
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
                    element = UMLPackage(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.CLASS:
                    element = UMLClass(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PORT:
                    element = UMLPort(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id, None,
                                      self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.AGGREGATION))

                elif xmi_type == XMITypeTypes.CONSTRAINT:
                    element = UMLConstraint(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PROPERTY:
                    element = UMLProperty(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PRIMITIVE_TYPE:
                    element = UMLPrimitiveType(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.HREF))

                elif xmi_type == XMITypeTypes.CONNECTOR:
                    element = UMLConnector(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.CONNECTOR_END:
                    element = UMLConnectorEnd(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.ROLE))

                elif xmi_type == XMITypeTypes.STATE_MACHINE:
                    element = UMLStateMachine(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.REGION:
                    element = UMLRegion(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.STATE:
                    element = UMLState(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.PSEUDO_STATE:
                    element = UMLPseudoState(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id,
                                             self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.KIND))

                elif xmi_type == XMITypeTypes.FINAL_STATE:
                    element = UMLFinalState(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)

                elif xmi_type == XMITypeTypes.TRANSITION:
                    element = UMLTransition(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.SOURCE),
                                            self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.TARGET))

                elif xmi_type == XMITypeTypes.TRIGGER:
                    event_id = self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.EVENT)
                    element = UMLTrigger(xmi_id, event_id)
                    aux = self.triggers.get(event_id, None)
                    if aux is None:
                        self.triggers[event_id] = [element]
                    else:
                        self.triggers[event_id].append(element)

                elif xmi_type == XMITypeTypes.CHANGE_EVENT:
                    element = UMLChangeEvent(self.get_tag_attr(tag.attrib, XMLTagAttributeTypes.NAME), xmi_id)
                    for trigger in self.triggers[xmi_id]:
                        trigger.event = element

        self.ids[xmi_id] = element
        if element is not None:
            for child in tag:
                parsed_child = self.parse_tag(child)
                if parsed_child is not None:
                    element.add_children(parsed_child)
        return element
