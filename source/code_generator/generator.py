class Generator:
    def __init__(self):
        self.imports = ['from utils.helpers import *\n']
        self.classes = []

    def add_import(self, file, elem):
        self.imports.append(f'from {file} import {elem}\n')

    def add_class(self, class_code):
        self.classes.append(class_code)

    def get_code(self):
        imports = ''.join(self.imports)
        classes = '\n'.join(self.classes)
        return '\n\n'.join([imports, classes])


class CodeGenerator:
    def __init__(self, level=0, indentation='    '):
        self.indentation = indentation
        self.level = level
        self.code = ''
        self.isInherited = False

    def indent(self):
        self.level += 1

    def dedent(self):
        self.level -= 1

    def create_class(self, name, inherited=None):
        if inherited is not None:
            self.add_code(f'class {name}({inherited}):\n')
            self.isInherited = True
        else:
            self.add_code(f'class {name}:\n')
        self.indent()

    def add_init_mode(self, properties, function_calls=None):
        if len(properties) == 0 and function_calls is None:
            return

        self.add_code("def __init__(self):\n")
        self.indent()
        if self.isInherited:
            self.add_code("super().__init__()\n")
        for prop, val in properties.items():
            self.add_code(f"self.{prop} = {val}\n")

        if function_calls is not None:
            for call in function_calls:
                self.add_code(call)
        self.add_code('\n')
        self.dedent()

    def add_method(self, name, code):
        self.add_code(f'def {name}:\n')
        self.indent()
        code = code.replace('\n', '\n' + self.indentation * self.level)
        self.add_code(code)
        self.dedent()
        self.add_code('\n')

    def add_code(self, code):
        if code == '\n':
            self.code += '\n'
        else:
            self.code += self.indentation * self.level + code

    def get_code(self):
        return self.code
