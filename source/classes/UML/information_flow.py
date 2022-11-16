from .basic import Basic


class InformationFlow(Basic):
    def __init__(self, name, xmi_id, source, target):
        super().__init__(name, xmi_id)
        self.source = source
        self.target = target

    def add_child(self, child):
        pass
