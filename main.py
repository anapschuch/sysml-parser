import plantuml
import sys
from source.generator import SysMLParser, generate_output_files

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        exit("Usage: main.py [file] [block]")

    plant_uml_server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
    parser = SysMLParser(args[0])
    root = parser.root

    for node in root:
        child_parsed = parser.parse_tag(node)

    block = None
    for b in parser.blocks:
        if b.name == args[1]:
            block = b

    if block is None:
        exit("Block '" + args[1] + "' not found")
    generate_output_files(block, parser, plant_uml_server)
