import os
import shutil

from source import *

helper_file_content = "\
import math \n\
from scipy.interpolate import * \n\
import numpy as np\n\n\n\
class Pointer:\n\
    def __init__(self, value): \n\
        self.value = value \n\n\n\
class ConstraintBlock:\n\
    def __init__(self): \n\
        self.ids = {} \n\
        self.attrs = {} \n\n\
    def add_input_port(self, port_id, port_name): \n\
        self.ids[port_id] = port_name \n\n\
    def add_input_port_value(self, port_id, port_value):\n\
        if port_id not in self.ids: \n\
            raise Exception(\"Unexpected port_id: \", port_id) \n\
        self.attrs[self.ids[port_id]] = port_value\n\n\
    def add_output_port(self, port_id, port_name):\n\
        self.ids[port_id] = port_name\n\
        self.attrs[port_name] = Pointer(None)\n\n\
    def get_output_port(self, port_id):\n\
        if port_id not in self.ids:\n\
            raise Exception(\"Unexpected port_id: \", port_id)\n\
        return self.attrs[self.ids[port_id]]\n"


def print_blocks_info():
    print("********* Blocks *********")
    for class_elem in parser.blocks:
        print("\n  Attributes:")
        print(class_elem.name)
        for attr in class_elem.attributes.values():
            attr.print(4)
        print("\n  Connectors:")
        for end1, end2 in class_elem.connectors.items():
            print("    ", end1, ": ", end2, sep="")
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
    constraint_gen.create_class(constraint_element.name.replace(' ', ''), 'ConstraintBlock')

    properties = {}
    ports = {'in': [], 'out': []}
    for attr in constraint_element.attributes.values():
        if type(attr) is Port:
            ports[attr.direction].append(attr)
        elif type(attr) is Property:
            properties[attr.name] = attr.default_value

    function_calls = []
    for port_in in ports['in']:
        function_calls.append(f'self.add_input_port(\'{port_in.xmi_id}\', \'{port_in.name}\')\n')

    for port_out in ports['out']:
        function_calls.append(f'self.add_output_port(\'{port_out.xmi_id}\', \'{port_out.name}\')\n')

    constraint_gen.add_init_mode(properties, function_calls)

    def replace_identifier(matchobj):
        if matchobj[0] in constraint_element.attribute_names:
            return f'self.attrs[\'{matchobj[0]}\'].value'
        else:
            return matchobj[0]

    specifications = []
    for c in constraint_element.constraints:
        spec = c.specification
        print(spec)

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
        f = open(output_folder_path + "{name}.py".format(name=class_name_file), "x")

        gen = Generator()
        class_gen = ClassGenerator()
        class_gen.create_class(class_elem.name.replace(' ', ''))

        properties = {}
        for attr in class_elem.attributes.values():
            if type(attr) is Property:
                properties[attr.name] = str(f'Pointer({attr.default_value})')

        for inner_class in class_elem.children.values():
            if inner_class.type == ClassType.BLOCK:
                file_name = convert_to_file_name(inner_class.name)
                class_name = inner_class.name.replace(' ', '')
                gen.add_import(file_name, class_name)
                properties[file_name] = class_name + '()'

            if inner_class.type == ClassType.CONSTRAINT_BLOCK:
                gen.add_class(generate_constraint_code(inner_class))

        class_gen.add_init_mode(properties)
        gen.add_class(class_gen.get_code())
        f.write(gen.get_code())
        f.close()


if __name__ == '__main__':
    parser = SysMLParser('examples/TransmissionSystem.uml')
    root = parser.root

    for node in root:
        child_parsed = parser.parse_tag(node)

    generate_output_files()
