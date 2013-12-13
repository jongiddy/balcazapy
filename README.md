# Balcazapy
Create a Taverna workflow file (t2flow format) using a script.

## Installation

### Linux
On Linux, run:
```
setup.sh
```
This installs a command "balc" into the bin folder. Add the bin folder to your
PATH, copy the "balc" executable to somewhere in your PATH, or reference "balc" with an absolute path name.

### Windows

On Windows, check values in setup.bat, then run:
```
setup.bat
```

This installs a command "balc" into the bin folder. Add the bin folder to your
PATH, copy the "balc" executable to somewhere in your PATH, or reference "balc" 
with an absolute path name.

## Creating a Balcazapy Description File
Balcazapy files are Python files. Hence, they have a .py suffix. Using the Python format allow them, to be edited in highlighting editors, including Idle, the editor that comes with Python.

### Prologue
Python requires that (almost) all names used but not defined in a file, are imported from libraries. To make use of Balcazar, start with these lines:

```python
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *
```

### Activities

Activities are the boxes you see in a workflow. Activities describe a particular task to be performed. There are several types of activities.

#### Beanshell

Create using:

```
BeanshellCode(script, inputs=dict(in1=List[String]), output=dict(out1=String))
```

or

```
BeanshellFile('file.bsh', inputs=dict(in1=List[String]), output=dict(out1=String)))
```

#### Interaction Pages

Create using:

```
InteractionPage(url)
```

#### Text Constant
Create using:

```
TextConstant(text)
```

#### RServe Scripts

For RServe scripts, first create an RServer using

```
rserve = RServer(host, port)
```

If port is omitted, the default RServe port (6311) will be used.

If host is omitted, localhost will be used.

Create an RServe script using

```
rserve.code('x <- y', inputs=dict(y=Vector[Integer]), outputs=dict(x=Vector[Integer])
```

or

```
rserve.file('file.r')
```

### Tasks

Essentially, "activities" can be created and assigned to named workflow tasks.
Activities can be reused, by assigning them to multiple tasks.

Each task has inputs and outputs, which have a type (e.g. String, Number).
Lists can be represented using List(String) or List(List(Number)).

Link input and output ports using the >> operator.

### Input and output ports

## Creating a Taverna 2 Workflow (t2flow) file

To create a t2flow file, run the command:

```
balc myfile.py myflow.t2flow
```

