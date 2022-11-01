from source import Class


def print_blocks_info(parser):
    print("********* Items Flow *********")
    for source, targets in parser.items_flow.items():
        base_source_elem = parser.ids[source]
        for target in targets:
            base_target_elem = parser.ids[target]
            print(f'{base_source_elem.name}  {source} ----> {base_target_elem.name} '
                  f' {target}')

    print("\n********* Blocks *********")
    for class_elem in parser.blocks:
        print(class_elem.name)
        print("\n  Attributes:")
        for attr in class_elem.attributes.values():
            attr.print(4)

        print("\n  Children:")
        for child_id, child_element in class_elem.children.items():
            if child_element is not None:
                print("     ", child_element.get_type(), ": ", child_element.name, sep="")
                if type(child_element) is Class and len(child_element.constraints) > 0:
                    print("          Parameters:")
                    for attr in child_element.attributes.values():
                        attr.print(12)
                    print("          Constraints:")
                    for constraint in child_element.constraints:
                        print("            ", constraint.specification)

        if class_elem.state_machine is not None:
            print("\n  State Machine:")
            class_elem.state_machine.print(5, parser.events)
        print("")
