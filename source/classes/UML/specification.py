from .body import Body


class Specification:
    def __init__(self, xmi_id):
        self.xmi_id = xmi_id
        self.language = "C"
        self.text = None

    def add_children(self, child):
        if type(child) is Body:
            if self.text is not None:
                raise Exception("Can only have one body in a specification tag")
            self.text = child.text
        else:
            raise Exception("Unexpected child for Specification tag")
