class Trigger:
    def __init__(self, xmi_id, event_id):
        self.xmi_id = xmi_id
        self.event_id = event_id
        self.event = None

    def add_event(self, event):
        self.event = event

    def print(self, indentation):
        if self.event is not None:
            print(' ' * indentation, self.event.change_expression["body"])
        else:
            raise Exception("Trigger event is empty. Trigger id: ", self.xmi_id)
