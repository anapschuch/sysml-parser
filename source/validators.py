from .classes import *


def validate_element(element):
    if type(element) is Property:
        if element.default_value is None:
            raise Exception("Default value must be set for all properties. Not set in '" +
                            element.name + "', id " + element.xmi_id)
    if type(element) is DefaultValue:
        if element.value is None:
            raise Exception("Empty default value: " + element.xmi_id)


