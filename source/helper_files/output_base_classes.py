class Basic:
    def __init__(self):
        self.ids = {}
        self.attrs = {}
        self.inputs = {}

    def add_property(self, property_id, name, value):
        self.ids[property_id] = name
        self.attrs[name] = value

    def add_port(self, port_id, name):
        self.ids[port_id] = name

    def set_port_value(self, port_name, port_value):
        self.attrs[port_name] = port_value

    def set_attr_value_id(self, attr_id, attr_value):
        if attr_id not in self.ids:
            raise Exception('Unknown attribute id ' + attr_id)
        attr_name = self.ids[attr_id]
        self.attrs[attr_name] = attr_value

    def get_output_port(self, port_name):
        if port_name not in self.attrs:
            raise Exception(f"Value not found for port '{port_name}'")
        return self.attrs[port_name]

    def get_attr_by_id(self, attr_id):
        if attr_id not in self.ids:
            raise Exception("Attribute id not found " + attr_id)
        name = self.ids[attr_id]
        if name not in self.attrs:
            return None
        return self.attrs[name]

    def check_if_all_values_are_set(self):
        for port_id in self.inputs:
            port_name = self.ids[port_id]
            if port_name not in self.attrs:
                return False
            if self.attrs[port_name] is None:
                return False
        return True


class ConstraintBlock(Basic):
    def __init__(self):
        super().__init__()


class Block(Basic):
    def __init__(self):
        super().__init__()
        self.inner_classes = {}
        self.update_order = {}
        self.inner_classes_connectors = {}
        self.attr_connectors = {}

    def add_inner_class(self, class_id, entity):
        self.inner_classes[class_id] = entity

    def update_state_machine(self):
        pass

    def update(self):
        self.update_state_machine()
        for element_id in self.update_order.keys():
            if element_id in self.inner_classes:
                inner_class = self.inner_classes[element_id]
                inner_class.update()
                if element_id not in self.inner_classes_connectors:
                    raise Exception("Inner class without output connectors: " + element_id)

                for conn in self.inner_classes_connectors[element_id]:
                    start = conn[0]
                    end = conn[1].split(' ')
                    val = inner_class.get_attr_by_id(start)
                    if val is None:
                        continue
                    if len(end) == 1:
                        self.set_attr_value_id(end[0], val)
                    elif len(end) == 2:
                        if end[0] not in self.inner_classes:
                            raise Exception("Error in inner class connector: " + end[0])
                        self.inner_classes[end[0]].set_attr_value_id(end[1], val)
                    else:
                        raise Exception("Unexpected length for inner class connector " + conn)
            else:
                if element_id not in self.ids:
                    raise Exception('Error: unexpected element id: ' + element_id)
                attr_name = self.ids[element_id]
                if attr_name not in self.attrs:
                    continue
                value = self.attrs[attr_name]
                if element_id not in self.attr_connectors:
                    continue
                for conn in self.attr_connectors[element_id]:
                    end = conn.split(' ')
                    if len(end) == 1:
                        self.set_attr_value_id(end[0], value)
                    elif len(end) == 2:
                        if end[0] not in self.inner_classes:
                            raise Exception("Error in inner class connector: " + end[0])
                        self.inner_classes[end[0]].set_attr_value_id(end[1], value)
                    else:
                        raise Exception("Unexpected length for inner class connector " + conn)
