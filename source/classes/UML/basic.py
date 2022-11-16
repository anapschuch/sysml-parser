class Basic:
    def __init__(self, name, xmi_id):
        self.name = name
        self.xmi_id = xmi_id
        self.children = dict()
        self.parent = None

    def add_child(self, child):
        if child is None:
            raise Exception("Error: trying to add a None child")
        self.children[child.xmi_id] = child

    def get_type(self):
        return type(self)
