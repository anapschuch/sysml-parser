class Trigger:
    def __init__(self, xmi_id, event_id):
        self.xmi_id = xmi_id
        self.event_id = event_id

    def print(self, indentation, events):
        event = events.get(self.event_id, None)
        if event is not None:
            print(' ' * indentation, event.change_expression["body"])
        else:
            raise Exception("Trigger event is empty. Trigger id: ", self.xmi_id)
