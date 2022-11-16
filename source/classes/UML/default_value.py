from .body import Body


class DefaultValue:
    def __init__(self, value_type, value, xmi_id):
        self.xmi_id = xmi_id
        self.value_type = value_type
        self.value = value
        if value is None:
            if value_type == "uml:LiteralReal":
                self.value = 0.0
            elif value_type == "uml:LiteralInteger":
                self.value = 0

    def add_child(self, child):
        if type(child) is Body:
            self.value = child.text
