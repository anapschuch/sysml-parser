from source import FinalState


class StateMachineGenerator:
    def __init__(self, level=0, indentation='  '):
        self.indentation = indentation
        self.level = level
        self.code = ''
        self.isInherited = False

    def indent(self):
        self.level += 1

    def dedent(self):
        self.level -= 1

    def add_code(self, code):
        self.code += self.indentation * self.level + code

    def create_state_chart(self, state_machine):
        self.add_code('statechart:\n')
        self.indent()
        self.add_code(f'name: {state_machine.name}\n')
        self.add_code(f'root state:\n')
        self.indent()

        # TODO: Add support for more regions (parallel states)
        self.add_region(state_machine.regions[0])

    def add_region(self, region, show_name=True):
        if show_name:
            self.add_code(f'name: {region.name}\n')
        if region.begin_state is None:
            raise Exception("Missing begin state for region " + region.name)

        if region.begin_state.xmi_id not in region.transitions:
            raise Exception("Missing transition from begin state in region " + region.name)

        begin_transitions = region.transitions[region.begin_state.xmi_id]
        if len(begin_transitions) > 1:
            raise Exception("Must have at most one transition from begin state - region " + region.name)

        first_state_id = begin_transitions[0].target
        first_state = region.states[first_state_id]
        self.add_code(f'initial: {first_state.name}\n')
        if len(region.states) > 1:
            self.add_code(f'states:\n')
            self.indent()
            for state_id, state in region.states.items():
                if state_id == region.begin_state.xmi_id:
                    continue
                self.add_code(f'- name: {state.name}\n')
                self.indent()
                if type(state) is FinalState:
                    self.add_code('type: final\n')
                if state.entry is not None:
                    self.add_code('on entry: |\n')
                    self.indent()
                    statements = state.entry.body.split('\r\n')
                    for stat in statements:
                        self.add_code(stat + '\n')
                    self.dedent()
                if state_id in region.transitions:
                    self.add_code('transitions:\n')
                    self.indent()
                    for trans in region.transitions[state_id]:
                        # TODO: Add guard actions
                        target_state = region.states[trans.target]
                        self.add_code(f'- target: {target_state.name}\n')
                        if trans.trigger is not None:
                            event = trans.trigger.event.name
                            self.indent()
                            self.add_code(f'event: {event}\n')
                            self.dedent()
                    self.dedent()
                self.dedent()
                if state.state_machine is not None:
                    self.indent()
                    # TODO: Add support for more regions
                    self.add_region(state.state_machine.regions[0], False)
                    self.dedent()
