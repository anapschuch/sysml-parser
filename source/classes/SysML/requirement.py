from .basic import *


class Requirement(Basic):
    def __init__(self, xmi_id, req_id, text, base_named_element, base_class):
        super().__init__(xmi_id)
        self.base_class = base_class
        self.base_named_element = base_named_element
        self.req_id = req_id
        self.text = text
        self.name = None

    def add_name(self, name):
        self.name = name
