# xml-parser

Hi there!

This project allows you to generate Python classes from a SysML model built with Papyrus. 

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
  --print     Use this option if you want to print information about the model in the terminal. You can use '> out.txt' at the end of the command to save it in a file
```

## Examples

<details>
<summary> Calculator

Inside the examples' folder, you can find the *Math.uml* file, which represents the Papyrus output from a model that 
has the following block:</summary>

![](public/Math-ParametricDiagram.png)

Basically,at each iteration, the z parameter in incremented by 0.01, and there are two outputs: y (the cos of z), 
and x (the sin of z). 

If you want to print information about the model, type in the terminal:

```bash
$ main.py ./examples/TransmissionSystem.uml System --print
```
</details>

To transform this model into Python classes, you can type:

```bash
$ main.py ./examples/TransmissionSystem.uml System
```

Two files will be generated inside the output folder: the *calculator.py* contains the Calculator block seen in the image above, 
while the *main.py* has the logic to simulate it. 

It's important to note that main has two simulation parameters set, the `dT` and `n_iter`, 
which are the time between two interactions, and the number of interactions, respectively. 
You can change it accordingly to your needs.

Additionally, by default, the *main.py* generates graphs of all output ports as a function of time. 
You can also change it as you desire.

To run this example, you can type:

 ```bash
$ python ./output/main.py 
```

Two graphs will be generated, one for each output port:

x             |  y
:-------------------------:|:-------------------------:
![](public/Math-x%20output.png) | ![](public/Math-y%20output.png)
