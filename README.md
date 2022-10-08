# xml-parser

Hi there!

This project allows you to generate Python classes from a SysML model built with Papyrus. 

## Running the project

First, clone or download this repository.

Create a virtual environment:

```bash
$ python -m venv ./venv
```

Activate the virtual environment:

**Linux/Mac:**
```bash
$ source ./venv/bin/activate
```

**Windows:**
```bash
$ venv/Scripts/activate
```

Install the project requirements:
```bash
$ python -m pip install -r requirements.txt
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
  --print     Use this option if you want to print the model info in the terminal.
              You can use '> out.txt' at the end of the command to save it in a file
```

## Examples

<details>
<summary> Calculator </summary>

Inside the examples' folder, you can find the *Math.uml* file, which represents the Papyrus output from a model that 
has the following block:

![](public/Math-ParametricDiagram.png)

Basically,at each iteration, the z parameter in incremented by 0.01, and there are two outputs: y (the cos of z), 
and x (the sin of z). 

If you want to print information about the model, type in the terminal:

```bash
$ python main.py ./examples/Math.uml Calculator --print
```

To transform this model into Python classes, you can type:

```bash
$ python main.py ./examples/Math.uml Calculator
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

</details>

<details>
<summary> Transmission System </summary>

**More details coming shortly!**

There is also a more complete example available. 
This one is about an automatic transmission system of a car, in which the driver can choose between the four usual 
modes: Parking, Reverse, Neutral and Drive.

This model is based on the work done by Antony Stark in his personal blog. Please take a look [here](https://x-engineer.org/vehicle-acceleration-maximum-speed-modeling-simulation/) if you require additional information.


![](public/System-Parametric%20Diagram.PNG)

It receives the following inputs:

* `dT`: time between two iterations of the simulation
* `env_cr`: road load coefficient
* `env_slope`: slope angle of the road the car is in
* `env_ro`: air density
* `env_cd`: drag coefficient
* `fa`: frontal area of the car
* `pedal position`: the percentage of the pedal that is pressed (a number between 0 and 100)
* `current gear`: the gear (Parking, Reverse, Neutral and Drive) that the driver is in. 
  Note that there is an order that must be followed to change gears, e.g. the driver cannot go to Drive directly 
  from Parking, they must go to Reverse and Neutral first. This logic is inside a state machine in the model, so the mode will
  be changed only if your input is correct.
  
These inputs must be given to the simulation in the form of a file. 
You can check the *examples/inputs_transmission_system.csv* file that is available. Each line of represents an iteration, 
and an empty cell means that the input hasn't changed.

There are two outputs in this system, the vehicle speed, and the drive gear. In the drive gear, 
we can see how the automatic transmission is working. 

To generate the python files for this example, type:

```bash
$ python main.py ./examples/TransmissionSystem.uml System
```

You must change the csv input in the *output/main.py* file. After that, move the terminal to the output folder and start the simulation:

 ```bash
$ cd output
$ python main.py 
```

Below is the outputs generated from the inputs given:

vehicle speed (m/s)        |  drive gear
:-------------------------:|:-------------------------:
![](public/TransmissionSystem-vehicle%20speed.png) | ![](public/TransmissionSystem-drive%20gear.png)
</details>


## How it works 

**This is a work in progress, it will be updated soon**
<details>
<summary> About the content of the Papyrus Project </summary>

If we look at the *.uml* file generated from Papyrus, we will see that it looks like the snippet below.

```xml
<ownedAttribute xmi:type="uml:Port" xmi:id="_WKF1QOESEeyXPMXG3lFeMw" name="env_cr" aggregation="composite">
    <type xmi:type="uml:PrimitiveType" href="pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#Real"/>
</ownedAttribute>
```

Basically, there are different tag types. Some examples are ownedAttribute, type, defaultValue and ownedRule. 
The current supported types can be seen [here](https://github.com/anapschuch/xml-parser/blob/main/source/xml_types/xml_tag.py#L4).

If we take a look at the .uml file, we will see that the project structure is built with UML types, while the SysML ones come at the end, and refer to some UML type. 
For example, for the port in the snippet above, we can see that it is the base port of a FlowPort:

```xml
<DeprecatedElements:FlowPort xmi:id="_WKHqcOESEeyXPMXG3lFeMw" base_Port="_WKF1QOESEeyXPMXG3lFeMw" direction="in"/>
```

This will be important when associating elements in the parser.

In addition to this, the tags also have different attributes, like xmi:type, xmi:id, name and base_Port. 
The current supported attributes can be seen [here](https://github.com/anapschuch/xml-parser/blob/main/source/xml_types/xml_tag_attribute.py#L4).
Furthermore, there are different *xmi_type* values, which the supported ones can be seen [here](https://github.com/anapschuch/xml-parser/blob/main/source/xml_types/xmi_type.py#L4).

In case you run the project and face an error about a not found type, you can add it in these files. 
Note that we chose to restrict the allowed types because they must be associated with some logic later. 
Having a type in these files doesn't mean the parser understands what it means and how it interacts with the other elements in the model. 
This will be covered in the next session.
</details>
