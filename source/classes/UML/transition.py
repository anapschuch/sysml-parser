from .trigger import Trigger


class Transition:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.trigger = None
        self.constraint = None

    def add_children(self, child):
        if type(child) is Trigger:
            self.trigger = child
        else:
            raise Exception("Unexpected child for UMLTransition: ", type(child))

    def print(self, indentation):
        print(' ' * indentation, self.source, "->", self.target)
        if self.constraint is not None:
            print(' ' * (indentation + 2), self.constraint.text)
        if self.trigger is not None:
            self.trigger.print(indentation+2)