from .basic import *


class Block(Basic):
    def __init__(self, xmi_id, base_class):
        super().__init__(xmi_id)
        self.base_class = base_class
