from source.globals import allowed_functions_from_external_libraries
from source.xml_types import XMLTagTypes, EnumPrimitiveType
from xml.etree import ElementTree
import re
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)


def parse_code_statement(attribute_names, specification, is_state_machine=False, error_message=''):
    def replace_identifier(match_obj):
        if is_state_machine:
            if match_obj[0] in attribute_names:
                return f'attrs[\'{match_obj[0]}\']'
        else:
            if match_obj[0] in attribute_names:
                return f'self.attrs[\'{match_obj[0]}\']'
        if match_obj[0] in allowed_functions_from_external_libraries:
            return match_obj[0]

        raise_error('Unexpected token: ' + match_obj[0] + f'\nStatement: \'{specification}\'\n' + error_message)
    return re.sub(r'([a-z]+(\.[a-z]+)+)|\b(?<!["\'])[a-zA-Z_][a-zA-Z0-9_]*\b', replace_identifier, specification)


def generate_importers_from_allowed_external_functions():
    libraries = {}
    for k, v in allowed_functions_from_external_libraries.items():
        if not v:
            continue
        libraries[v] = libraries.get(v, []) + [k]

    for k, v in libraries.items():
        libraries[k] = ", ".join(v)
    return [f'from {k} import {v}' for k, v in libraries.items()]


def is_tag_requirement_type(tag):
    return tag == XMLTagTypes.REQUIREMENT or tag == XMLTagTypes.REQUIREMENTS_REFINE or \
           tag == XMLTagTypes.REQUIREMENTS_SATISFY or tag == XMLTagTypes.REQUIREMENTS_VERIFY


def get_primitive_type(href):
    href_list = href.split("#")
    value = href_list[len(href_list) - 1]
    if value == "Real":
        return EnumPrimitiveType.REAL
    elif value == "Integer":
        return EnumPrimitiveType.INTEGER
    elif value == "Boolean":
        return EnumPrimitiveType.BOOLEAN
    elif value == "String":
        return EnumPrimitiveType.STRING
    else:
        raise Exception("Primitive type not found: " + value)


def convert_to_file_name(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2.replace(' ', '')


def get_xml_file_namespaces(filename):
    return dict([
        elem for _, elem in ElementTree.iterparse(filename, events=['start-ns'])
    ])


def raise_error(message):
    logging.error(message)
    exit(1)
