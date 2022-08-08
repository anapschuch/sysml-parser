from xml_types import XMLTagTypes


def is_tag_requirement_type(tag):
    return tag == XMLTagTypes.REQUIREMENT or tag == XMLTagTypes.REQUIREMENTS_REFINE or \
           tag == XMLTagTypes.REQUIREMENTS_SATISFY or tag == XMLTagTypes.REQUIREMENTS_VERIFY
