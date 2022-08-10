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
            for child_element in base_class_elem.children:
                if type(child_element) is UMLPort:
                    print("     ", child_element.name)
            print("")
