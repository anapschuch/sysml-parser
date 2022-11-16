from .trigger import Trigger


class Transition:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.trigger = None

    def add_child(self, child):
        if type(child) is Trigger:
            self.trigger = child
        else:
            raise Exception("Unexpected child for UMLTransition: ", type(child))

    def print(self, indentation, events):
        print(' ' * indentation, self.source, "->", self.target)

        if self.trigger is not None:
            self.trigger.print(indentation + 2, events)
