import os
import shutil
import plantuml
from sismic.io import import_from_yaml, export_to_plantuml

from source import *

helper_file_content = "\
import math \n\
from scipy.interpolate import * \n\
import numpy as np\n\n\n\
class Block:\n\
    def __init__(self): \n\
        self.ids = {} \n\
        self.attrs = {} \n\n\
    def add_property(self, property_id, name, value):\n\
        self.ids[property_id] = name\n\
        self.attrs[name] = value\n\n\
    def add_port(self, port_id, name): \n\
        self.ids[port_id] = name \n\n\
    def set_port_value(self, port_id, port_value): \n\
        if port_id not in self.ids: \n\
            raise Exception(\"Unexpected port_id: \", port_id) \n\
        self.attrs[self.ids[port_id]] = port_value \n\n\
    def get_output_port(self, port_id): \n\
        if port_id not in self.ids: \n\
            raise Exception(\"Unexpected port_id: \", port_id) \n\
        port_name = self.ids[port_id] \n\
        if port_name not in self.attrs: \n\
            raise Exception(f\"Value not found for port '{port_name}'\") \n\
        return self.attrs[self.ids[port_id]]\n"


def print_blocks_info():
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

        print("\n  Children Attributes:")
        for attr_id, attr_ref in class_elem.children_attributes.items():
            print("    ", attr_id, ": ", attr_ref.name, " (", attr_ref.xmi_id, ")", sep="")
        if class_elem.state_machine is not None:
            print("")
            class_elem.state_machine.print(2)
        print("\n  Children:")
        for child_id, child_element in class_elem.children.items():
            if child_element is not None:
                print("     ", type(child_element), ": ", child_element.name, sep="")
                if type(child_element) is Class and len(child_element.constraints) > 0:
                    print("          Parameters:")
                    for attr in child_element.attributes.values():
                        attr.print(12)
                    print("          Constraints:")
                    for constraint in child_element.constraints:
                        print("            ", constraint.specification)
        print("")


def generate_constraint_code(constraint_element):
    constraint_gen = ClassGenerator()
    constraint_gen.create_class(constraint_element.name.replace(' ', ''), 'Block')

    properties = {}
    ports = []
    for attr in constraint_element.attributes.values():
        if type(attr) is Port:
            ports.append(attr)
        elif type(attr) is Property:
            properties[attr.name] = attr.default_value

    function_calls = []
    for p in ports:
        function_calls.append(f'self.add_port(\'{p.xmi_id}\', \'{p.name}\')\n')

    constraint_gen.add_init_mode(properties, function_calls)

    def replace_identifier(match_obj):
        if match_obj[0] in constraint_element.attribute_names:
            return f'self.attrs[\'{match_obj[0]}\']'
        else:
            return match_obj[0]

    specifications = []
    for c in constraint_element.constraints:
        spec = c.specification
        spec = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*', replace_identifier, spec)
        specifications.append(spec)

    if len(specifications) > 0:
        constraint_gen.add_code('def update_constraint_value(self):\n')
        constraint_gen.indent()
        for spec in specifications:
            constraint_gen.add_code(spec + '\n')
        constraint_gen.add_code('\n')
        constraint_gen.dedent()

    return constraint_gen.get_code()


def aux_update_element_order(class_element, order_dict, current_order, element_id, visited):
    if element_id in visited:
        return

    if element_id in order_dict:
        order_dict[element_id] = max(current_order, order_dict[element_id])
    else:
        order_dict[element_id] = current_order
    visited.append(element_id)

    if element_id in class_element.children_attributes.keys():
        inner_class = class_element.children_attributes[element_id]
        inner_port = inner_class.attributes[element_id]
        if type(inner_port) is Port and inner_port.direction == 'out':
            for attr in inner_class.attributes.values():
                if type(attr) is Port and attr.direction == 'in':
                    aux_update_element_order(class_element, order_dict, current_order+1, attr.xmi_id, visited)

    connectors = parser.items_flow_reversed
    if element_id not in connectors:
        return

    for next_element_id in connectors[element_id]:
        aux_update_element_order(class_element, order_dict, current_order+1, next_element_id, visited)


def generate_update_elements_order(class_element):
    order = {}
    for attr in class_element.attributes.values():
        if type(attr) is Port and attr.direction == 'out':
            aux_update_element_order(class_element, order, 0, attr.xmi_id, [])

    blocks_order = {}
    for item_id in order.keys():
        if item_id in class_element.children_attributes.keys():
            inner_class = class_element.children_attributes[item_id]
            if inner_class.xmi_id not in blocks_order:
                blocks_order[inner_class.xmi_id] = order[item_id]
        else:
            blocks_order[item_id] = order[item_id]
    return blocks_order


def generate_output_files():
    output_folder_path = "./output/"
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.mkdir(output_folder_path)

    os.mkdir(output_folder_path+'utils/')
    f = open(output_folder_path + 'utils/helpers.py', "x")
    f.write(helper_file_content)
    f.close()

    for class_elem in parser.blocks:
        class_name_file = convert_to_file_name(class_elem.name)

        if class_elem.state_machine is not None:
            f = open(output_folder_path + f"{class_name_file}.yaml", "x")
            state_machine_code_gen = StateMachineGenerator()
            state_machine_code_gen.create_state_chart(class_elem.state_machine)
            f.write(state_machine_code_gen.code)
            f.close()

            f = open(output_folder_path + f"{class_name_file}.PNG", "wb")
            statechart = import_from_yaml(state_machine_code_gen.code)

            f.write(plant_uml_server.processes(export_to_plantuml(statechart)))
            f.close()

        f = open(output_folder_path + f"{class_name_file}.py", "x")

        gen = Generator()
        class_gen = ClassGenerator()
        class_gen.create_class(class_elem.name.replace(' ', ''), 'Block')

        properties = {}
        function_calls = []
        for attr in class_elem.attributes.values():
            if type(attr) is Port:
                function_calls.append(f'self.add_port(\'{attr.xmi_id}\', \'{attr.name}\')\n')
            elif type(attr) is Property:
                function_calls.append(f'self.add_property(\'{attr.xmi_id}\', \'{attr.name}\', {attr.default_value})\n')

        for inner_class in class_elem.children.values():
            if inner_class.type == ClassType.BLOCK:
                file_name = convert_to_file_name(inner_class.name)
                class_name = inner_class.name.replace(' ', '')
                gen.add_import(file_name, class_name)
                properties[file_name] = class_name + '()'

            if inner_class.type == ClassType.CONSTRAINT_BLOCK:
                gen.add_class(generate_constraint_code(inner_class))

        update_order = generate_update_elements_order(class_elem)
        update_order_sorted = dict(sorted(update_order.items(), key=lambda item: item[1], reverse=True))
        properties['update_order'] = update_order_sorted

        class_gen.add_init_mode(properties, function_calls)
        gen.add_class(class_gen.get_code())
        f.write(gen.get_code())
        f.close()


if __name__ == '__main__':
    plant_uml_server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')

    parser = SysMLParser('examples/TransmissionSystem.uml')
    root = parser.root

    for node in root:
        child_parsed = parser.parse_tag(node)

    generate_output_files()