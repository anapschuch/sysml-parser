from source import FinalState, parse_code_statement
from .generator import CodeGenerator


class StateMachineGenerator(CodeGenerator):
    def __init__(self, block_name, level=0, indentation='  '):
        super().__init__(level, indentation)
        self.block = block_name

    def create_state_chart(self, state_machine, attributes, events):
        self.add_code('statechart:\n')
        self.indent()
        self.add_code(f'name: {state_machine.name}\n')
        self.add_code(f'root state:\n')
        self.indent()

        # TODO: Add support for more regions (parallel states)
        self.add_region(state_machine.regions[0], attributes, state_machine.name, events)

    def add_region(self, region, attributes, state_machine_name, events, show_name=True):
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
                        error_location = f'Location: \nEntry behavior of state \'{state.name}\'\n' \
                                        f'    inside state machine \'{state_machine_name}\'\n' \
                                        f'        of block \'{self.block}\''
                        self.add_code(parse_code_statement(attributes, stat, True, error_location) + '\n')
                    self.dedent()
                if state_id in region.transitions:
                    self.add_code('transitions:\n')
                    self.indent()
                    for trans in region.transitions[state_id]:
                        # TODO: Add guard actions
                        target_state = region.states[trans.target]
                        self.add_code(f'- target: {target_state.name}\n')
                        if trans.trigger is not None:
                            event = events[trans.trigger.event_id].name
                            self.indent()
                            self.add_code(f'event: {event}\n')
                            self.dedent()
                    self.dedent()
                self.dedent()
                if state.state_machine is not None:
                    self.indent()
                    # TODO: Add support for more regions
                    self.add_region(state.state_machine.regions[0], attributes, state.state_machine.name, events, False)
                    self.dedent()
            self.dedent()