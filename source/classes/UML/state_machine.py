from .basic import Basic
from .transition import Transition
from .pseudo_state import PseudoState, PseudoStateTypes
from .final_state import FinalState
from .state_entry_behavior import StateEntryBehavior


class StateMachine(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.regions = []

    def add_child(self, child):
        if type(child) is Region:
            self.regions.append(child)
        else:
            raise Exception("Unexpected child for UMLStateMachine: ", type(child))

    def print(self, indentation, events):
        print(' ' * indentation, "State Machine: ", self.name, sep="")
        for region in self.regions:
            region.print(indentation + 2, events)


class Region(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.transitions = dict()
        self.begin_state = None
        self.end_state = None
        self.states = dict()

    def add_child(self, child):
        if type(child) is Transition:
            if child.source in self.transitions:
                self.transitions[child.source].append(child)
            else:
                self.transitions[child.source] = [child]
        elif type(child) is State:
            self.states[child.xmi_id] = child
        elif type(child) is PseudoState:
            if child.kind == PseudoStateTypes.BEGIN:
                self.begin_state = child
            self.states[child.xmi_id] = child
        elif type(child) is FinalState:
            self.end_state = child
            self.states[child.xmi_id] = child
        else:
            raise Exception("Unexpected child for UMLRegion: ", type(child))

    def print(self, indentation, events):
        print(' ' * indentation, "Region ", self.name, ":", self.xmi_id, sep="")
        for state in self.states.values():
            state.print(indentation + 2, events)

        if len(self.transitions) > 0:
            print("\n" + ' ' * indentation, "Transitions: ", sep="")
            for transitions in self.transitions.values():
                for trans in transitions:
                    trans.print(indentation, events)


class State(Basic):
    def __init__(self, name, xmi_id):
        super().__init__(name, xmi_id)
        self.state_machine = None
        self.entry = None

    def add_child(self, child):
        if type(child) is StateMachine:
            if self.state_machine is not None:
                raise Exception("Expect at most one state machine in a state")
            self.state_machine = child
        elif type(child) is StateEntryBehavior:
            if self.entry is not None:
                raise Exception("Expect at most one entry behavior in state")
            self.entry = child
        else:
            raise Exception("Unexpected child for UMLState: ", type(child))

    def print(self, indentation, events):
        print(' ' * indentation, self.name, ":", self.xmi_id, sep="")
        if self.entry is not None:
            txt = self.entry.body
            txt = txt.replace('\r\n', '\n' + ' ' * (indentation + 9))
            print(' ' * (indentation + 2), "entry: ", txt, sep="")
        if self.state_machine is not None:
            self.state_machine.print(indentation + 2, events)
