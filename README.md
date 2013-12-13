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
### Types

For input and output ports, and for some activities, you will need to specify a 
type for a port.

Available types are:
- String
- Integer
- Number
- TextFile
- PDF_File
- PNG_Image

For RServe activities, you can also specify:
- Logical
- RExpression
- Vector[Logical]
- Vector[Integer]
- Vector[Number]
- Vector[String]

You can also specify lists using List[type], where type is any of the above, or
another list.

e.g.
- List[Integer] - a list of integers
- List[RExpression] - a list of RExpressions
- List[List[String]] - a list containing lists of strings


### Activities

Activities are the boxes you see in a workflow. Activities describe a particular task to be performed. There are several types of activities.

#### Beanshell

Create using:

```python
BeanshellCode(
	script,
	inputs=dict(in1=List[String]),
	output=dict(out1=String)
	)
```

or

```python
BeanshellFile(
	'file.bsh',
	inputs=dict(in1=List[String]),
	output=dict(out1=String))
	)
```

#### Interaction Pages

Create using:

```python
InteractionPage(url)
```

#### Text Constant
Create using:

```python
TextConstant('Some text')
```

#### RServe Scripts

For RServe scripts, first create an RServer using

```python
rserve = RServer(host, port)
```

If port is omitted, the default RServe port (6311) will be used.

If host is omitted, localhost will be used.

Create an RServe script using

```python
rserve.code(
	'x <- y',
	inputs=dict(y=Vector[Integer]),
	outputs=dict(x=Vector[Integer])
	)
```

or

```python
rserve.file('file.r')
```

For RServe activities, you do not need to specify an input or output port, if it
is an RExpression.

### Tasks

Activities can be created and assigned to named workflow tasks.
Activities can be reused, by assigning them to multiple tasks.

```python
flow.task.MyTask = rserve.code(
	'x <- y',
	inputs=dict(y=Vector[Integer]),
	outputs=dict(x=Vector[Integer])
	)
```

### Input and output ports

Link input and output ports using the >> operator.

```python
flow.input.InputValue = List[Integer]
flow.input.InputValue >> flow.task.MyTask.input.y

flow.output.OutputValue = List[Integer]
flow.task.MyTask.output.x >> flow.output.OutputValue
```

### Shortcuts

To assign an input or output port with the same type as an activity port, use the
equals sign. The example above could be created as:

```python
flow.input.InputValue = flow.task.MyTask.input.y

flow.output.OutputValue = flow.task.MyTask.output.x
```

The types are inferred from the activity types (R Vector becomes a List).

To connect all unconnected ports of a task as ports of the workflow, use:

```python
flow.task.MyTask.extendUnusedInputs()
flow.task.MyTask.extendUnusedOutputs()
```

or, even shorter, for the above case:

```python
flow.task.MyTask.extendUnusedPorts()
```

## Creating a Taverna 2 Workflow (t2flow) file

To create a t2flow file, run the command:

```
balc myfile.py myflow.t2flow
```

