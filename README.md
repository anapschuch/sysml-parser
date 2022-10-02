# xml-parser

Hi there!

This project allows you to generate Python classes from a SysML model generated with Papyrus. 

## Running the project

First, clone the repository:


```bash
$ git clone git@github.com:anapschuch/xml-parser.git
```

Create a virtual environment:

```bash
$ python3 -m venv ./venv
```

Activate the virtual environment and install the project requirements:
```bash
$ source ./venv/bin/activate
$ python3 -m pip install -r requirements.txt
```

To run the project, you need to specify the input file (the .uml generated from Papyrus project),
and the block you want to simulate. See the options available below:
```
usage: main.py [-h] [--print] file block

positional arguments:
  file        The .uml file generated from the Papyrus project
  block       The block you want to simulate

optional arguments:
  -h, --help  show this help message and exit
  --print     Use this option if you want to print the model info in the terminal. You can use '> out.txt' at the end of the command to save it in a file
```