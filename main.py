import os
import shutil
import plantuml
import sys
from sismic.io import import_from_yaml, export_to_plantuml

from source import *


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
    constraint_gen = CodeGenerator()
    constraint_gen.create_class(constraint_element.name.replace(' ', ''), 'ConstraintBlock')

    properties = {}
    ports = []
    input_ports = []
    for attr in constraint_element.attributes.values():
        if type(attr) is Port:
            ports.append(attr)
            if attr.direction == 'in':
                input_ports.append(attr.xmi_id)
        elif type(attr) is Property:
            properties[attr.name] = attr.default_value

    properties['inputs'] = input_ports
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
        constraint_gen.add_code('def update(self):\n')
        constraint_gen.indent()
        constraint_gen.add_code('if not self.check_if_all_values_are_set():\n')
        constraint_gen.indent()
        constraint_gen.add_code('return\n\n')
        constraint_gen.dedent()
        for spec in specifications:
            constraint_gen.add_code(spec + '\n')
        constraint_gen.add_code('\n')
        constraint_gen.dedent()

    return constraint_gen.get_code()


def aux_update_element_order(class_element, order_dict, current_order, element_id, visited,
                             inner_classes_connectors, attr_connectors):
    if element_id in order_dict:
        order_dict[element_id] = max(current_order, order_dict[element_id])
    else:
        order_dict[element_id] = current_order

    if element_id in visited:
        return
    visited.append(element_id)

    element_id_complete = element_id
    if element_id in class_element.children_attributes.keys():
        inner_class = class_element.children_attributes[element_id]
        inner_port = inner_class.attributes[element_id]
        element_id_complete = f'{inner_class.xmi_id} {element_id}'
        if type(inner_port) is Port and inner_port.direction == 'out':
            for attr in inner_class.attributes.values():
                if type(attr) is Port and attr.direction == 'in':
                    aux_update_element_order(class_element, order_dict, current_order + 1, attr.xmi_id, visited.copy(),
                                             inner_classes_connectors, attr_connectors)
            return

    else:
        element = parser.ids[element_id]
        if type(element) is Port and element.direction == 'in':
            return

    connectors = parser.items_flow_reversed
    if element_id not in connectors:
        return

    for next_element_id in connectors[element_id]:
        next_element_id_complete = next_element_id
        if next_element_id in class_element.children_attributes.keys():
            inner_class = class_element.children_attributes[next_element_id]
            if inner_class.xmi_id not in inner_classes_connectors:
                inner_classes_connectors[inner_class.xmi_id] = [[next_element_id_complete, element_id_complete]]
            elif [next_element_id_complete, element_id_complete] not in inner_classes_connectors[inner_class.xmi_id]:
                inner_classes_connectors[inner_class.xmi_id].append([next_element_id_complete, element_id_complete])
        else:
            if next_element_id_complete not in attr_connectors:
                attr_connectors[next_element_id_complete] = [element_id_complete]
            elif element_id_complete not in attr_connectors[next_element_id_complete]:
                attr_connectors[next_element_id_complete].append(element_id_complete)

        aux_update_element_order(class_element, order_dict, current_order + 1, next_element_id, visited.copy(),
                                 inner_classes_connectors, attr_connectors)


def generate_update_elements_order(class_element):
    order = {}
    attr_connectors = {}
    inner_classes_connectors = {}
    for attr in class_element.attributes.values():
        if type(attr) is Port and attr.direction == 'out':
            aux_update_element_order(class_element, order, 0, attr.xmi_id, [],
                                     inner_classes_connectors, attr_connectors)

    blocks_order = {}
    for item_id in order.keys():
        if item_id in class_element.children_attributes.keys():
            inner_class = class_element.children_attributes[item_id]
            if inner_class.xmi_id not in blocks_order:
                blocks_order[inner_class.xmi_id] = order[item_id]
            else:
                blocks_order[inner_class.xmi_id] = min(blocks_order[inner_class.xmi_id], order[item_id])
        else:
            element = parser.ids[item_id]
            if not (type(element) is Port and element.direction == 'out'):
                blocks_order[item_id] = order[item_id]
    return {
        'blocks_order': blocks_order,
        'inner_classes_connectors': inner_classes_connectors,
        'attr_connectors': attr_connectors
    }


def generate_main_file(block):
    f = open('./output/main.py', "x")
    gen = CodeGenerator()
    file_name = convert_to_file_name(block.name)
    class_name = block.name.replace(' ', '')
    gen.add_code(f'from {file_name} import {class_name}\n\n')
    gen.add_code('if __name__ == \'__main__\':\n')
    gen.indent()

    block_var_name = file_name
    gen.add_code(f'{block_var_name} = {class_name}()\n\n')
    gen.add_code('# set the port values below\n')
    for attr in block.attributes.values():
        if type(attr) is Port and attr.direction == 'in':
            gen.add_code(f'{block_var_name}.set_port_value(\'{attr.name}\', 0)\n')

    gen.add_code('\n')
    gen.add_code(f'{block_var_name}.update()\n\n')

    for attr in block.attributes.values():
        if type(attr) is Port and attr.direction == 'out':
            gen.add_code(f'print({block_var_name}.get_output_port(\'{attr.name}\'))\n')

    f.write(gen.get_code())
    f.close()


def get_state_machine_events(state_machine, events):
    for region in state_machine.regions:
        for transitions in region.transitions.values():
            for single_transition in transitions:
                if single_transition.trigger is not None:
                    event = single_transition.trigger.event
                    events[event.name] = event.change_expression['body']

        for state in region.states.values():
            if type(state) is State and state.state_machine is not None:
                get_state_machine_events(state.state_machine, events)


def get_state_machine_events_params(events):
    params_set = set()
    for event_expression in events.values():
        params_expression = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', event_expression)
        for param in params_expression:
            if param not in params_set:
                params_set.add(param)

    return params_set


def generate_output_files(block):
    output_folder_path = "./output/"
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.mkdir(output_folder_path)

    os.mkdir(output_folder_path + 'utils/')
    shutil.copyfile('source/helper_files/output_base_classes.py', output_folder_path + 'utils/helpers.py')

    generate_main_file(block)

    for class_elem in parser.blocks:
        class_name_file = convert_to_file_name(class_elem.name)

        f = open(output_folder_path + f"{class_name_file}.py", "x")

        gen = Generator()
        class_gen = CodeGenerator()
        class_gen.create_class(class_elem.name.replace(' ', ''), 'Block')

        properties = {}
        function_calls = []
        input_ports = []
        for attr in class_elem.attributes.values():
            if type(attr) is Port:
                function_calls.append(f'self.add_port(\'{attr.xmi_id}\', \'{attr.name}\')\n')
                if attr.direction == 'in':
                    input_ports.append(attr.xmi_id)
            elif type(attr) is Property:
                function_calls.append(f'self.add_property(\'{attr.xmi_id}\', \'{attr.name}\', {attr.default_value})\n')
        properties['inputs'] = input_ports

        for inner_class_id, inner_class in class_elem.children.items():
            inner_class_name = inner_class.name.replace(' ', '')
            function_calls.append(f'self.add_inner_class(\'{inner_class_id}\', {inner_class_name}())\n')

            if inner_class.type == ClassType.BLOCK:
                file_name = convert_to_file_name(inner_class.name)
                gen.add_import(file_name, inner_class_name)

            if inner_class.type == ClassType.CONSTRAINT_BLOCK:
                gen.add_class(generate_constraint_code(inner_class))

        state_machine_code_gen = None
        if class_elem.state_machine is not None:
            f_state_machine = open(output_folder_path + f"{class_name_file}.yaml", "x")
            state_machine_code_gen = StateMachineGenerator()
            state_machine_code_gen.create_state_chart(class_elem.state_machine, class_elem.attribute_names)
            f_state_machine.write(state_machine_code_gen.code)
            f_state_machine.close()

            f_state_machine = open(output_folder_path + f"{class_name_file}.PNG", "wb")
            statechart = import_from_yaml(state_machine_code_gen.code)

            events = {}
            get_state_machine_events(class_elem.state_machine, events)

            gen.add_import('sismic.io', 'import_from_yaml')
            gen.add_import('sismic.interpreter', 'Interpreter')
            sm_class_var = f'{class_name_file}_sm'
            properties[sm_class_var] = 'Interpreter(import_from_yaml(' \
                                       f'filepath=\'./{class_name_file}.yaml\'), ' \
                                       'initial_context={\'attrs\': self.attrs})'

            state_machine_code_gen = CodeGenerator()
            state_machine_code_gen.add_code(f'if not self.check_if_all_values_are_set():\n')
            state_machine_code_gen.indent()
            state_machine_code_gen.add_code('return\n')
            state_machine_code_gen.dedent()

            def replace_identifier(match_obj):
                if match_obj[0] in class_elem.attribute_names:
                    return f'self.attrs[\'{match_obj[0]}\']'
                else:
                    return match_obj[0]

            for event_name, event_code in events.items():
                code = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*', replace_identifier, event_code)

                state_machine_code_gen.add_code(f'if {code}:\n')
                state_machine_code_gen.indent()
                state_machine_code_gen.add_code(f'self.{sm_class_var}.queue(\'{event_name}\')\n')
                state_machine_code_gen.dedent()
            state_machine_code_gen.add_code(f'self.{sm_class_var}.execute()')

            f_state_machine.write(plant_uml_server.processes(export_to_plantuml(statechart)))
            f_state_machine.close()

        aux = generate_update_elements_order(class_elem)
        update_order = aux['blocks_order']
        inner_classes_connectors = aux['inner_classes_connectors']
        attr_connectors = aux['attr_connectors']
        update_order_sorted = dict(sorted(update_order.items(), key=lambda item: item[1], reverse=True))
        properties['update_order'] = update_order_sorted
        properties['inner_classes_connectors'] = inner_classes_connectors
        properties['attr_connectors'] = attr_connectors

        class_gen.add_init_mode(properties, function_calls)
        if state_machine_code_gen is not None:
            class_gen.add_method('update_state_machine(self)', state_machine_code_gen.code)
        gen.add_class(class_gen.get_code())
        f.write(gen.get_code())
        f.close()


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        exit("Usage: main.py [file] [block]")

    plant_uml_server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
    parser = SysMLParser(args[0])
    root = parser.root

    for node in root:
        child_parsed = parser.parse_tag(node)

    block = None
    for b in parser.blocks:
        if b.name == args[1]:
            block = b

    if block is None:
        exit("Block '" + args[1] + "' not found")
    generate_output_files(block)
