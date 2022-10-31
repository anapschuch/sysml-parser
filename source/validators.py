from . import raise_error
from .classes import *


def validate_element(element, parent):
    if type(element) is Property:
        if element.default_value is None:
            raise_error(f"Default value must be set for all properties. \nNot set in '{element.name}'\n"
                        f"Location: '{parent.name}'")
    if type(element) is DefaultValue:
        if element.value is None:
            raise_error(f"Empty default value: {element.xmi_id}")
