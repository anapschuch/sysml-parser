import argparse
import plantuml

from source.generator import SysMLParser, generate_output_files
from source.information_printer import print_blocks_info

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(prog='main.py', formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument('file', help='The .uml file generated from the Papyrus project')
    arg_parser.add_argument('block', help='The block you want to simulate')
    arg_parser.add_argument('--print', action='store_true',
                            help='''Use this option if you want to print the model info in the terminal.
You can use \'> out.txt\' at the end of the command to save it in a file''')

    args = arg_parser.parse_args()

    plant_uml_server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
    parser = SysMLParser(args.file)
    root = parser.root

    for node in root:
        child_parsed = parser.parse_tag(node, None)

    block = None
    for b in parser.blocks:
        if b.name == args.block:
            block = b

    if block is None:
        exit("Block '" + args.block + "' not found")

    if args.print:
        print_blocks_info(parser)
    else:
        generate_output_files(block, parser, plant_uml_server)
