import xml.etree.ElementTree as ElementTree

from xml_types import XMITypeTypes, XMLTagTypes, XMLTagAttributeTypes


class SysMLParser:
    def __init__(self, filename):
        self.filename = filename
        self.namespaces = self.get_namespaces()
        self.tag_types = self.get_tag_types_path(XMLTagTypes)
        self.tag_attributes = self.get_tag_types_path(XMLTagAttributeTypes)
        self.tag_xmi_types = {i.value: i.name for i in XMITypeTypes}
        self.root = ElementTree.parse(filename).getroot()

    def get_tag_types_path(self, types_list):
        tag_types = dict()
        for tag_type in list(types_list):
            path = self.get_tag_path(tag_type.value)
            tag_types[path] = tag_type
        return tag_types

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


if __name__ == '__main__':
    parser = SysMLParser('examples/TransmissionSystem.uml')
    root = parser.root

    stack = [root]
    while len(stack) > 0:
        node = stack.pop()
        for child in node:
            for attr in child.attrib:
                attr_type = parser.get_tag_attribute_type(attr)
                if attr_type == XMLTagAttributeTypes.XMI_TYPE:
                    print("xmi_type: ", parser.get_tag_xmi_type(child.attrib[attr]))
            stack.append(child)
