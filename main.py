from source import *

if __name__ == '__main__':
    parser = SysMLParser('examples/TransmissionSystem.uml')
    root = parser.root

    for node in root:
        child_parsed = parser.parse_tag(node)

    print("********* Blocks *********")
    for block in parser.blocks:
        base_class_id = block.base_class
        base_class_elem = parser.ids[base_class_id]
        if base_class_elem is not None and type(base_class_elem) is UMLClass:
            print(base_class_elem.name)
            print("\n  Attributes:")
            for attr_id, attr in base_class_elem.attributes.items():
                if type(attr) is UMLPort:
                    print("    Port (", attr.direction, "): ", attr_id, " - ", attr.name, sep="")
                else:
                    print("    Property:", attr_id, ": ", attr.name, sep="")

            print("\n  Connectors:")
            for end1, end2 in base_class_elem.connectors.items():
                print("    ", end1, ": ", end2, sep="")

            print("\n  Children Attributes:")
            for attr_id, attr_ref in base_class_elem.children_attributes.items():
                print("    ", attr_id, ": ", attr_ref.name, " (", attr_ref.xmi_id, ")", sep="")

            if base_class_elem.state_machine is not None:
                print("\n  State Machine:")
                print_state_machine(base_class_elem.state_machine, 4)

            print("\n  Children:")
            for child_id, child_element in base_class_elem.children.items():
                if child_element is not None:
                    print("     ", type(child_element), ": ", child_element.name, sep="")
            print("")
