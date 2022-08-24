from source.xml_types import XMLTagTypes, EnumPrimitiveType


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
    else:
        raise Exception("Primitive type not found: ", value)



