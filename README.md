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
Python requires that (almost) all names used but not defined in a file, are imported from libraries. To make use of Balcazapy, start with these lines:

```python
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *
```

### Workflows

Create a workflow using:

```python
flow = Workflow(title='Create Projection Matrix', author="Maria and Jon",
	description="Create a projection matrix from a stage matrix and a list of stages")

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

Activities are the boxes you see in a workflow. Activities describe a particular 
task to be performed. There are several types of activities.

#### Beanshell

Create using:

```python
BeanshellCode(
	"""String seperatorString = "\n";
if (seperator != void) {
	seperatorString = seperator;
}
StringBuffer sb = new StringBuffer();
for (Iterator i = stringlist.iterator(); i.hasNext();) {
	String item = (String) i.next();
	sb.append(item);
	if (i.hasNext()) {
		sb.append(seperatorString);
	}
}
concatenated = sb.toString();
""",
	inputs=dict(
		stringlist=List[String],
		seperator=String
		),
	output=dict(
		concatenated=String
		)
	)
```

or

```python
BeanshellFile(
	'file.bsh',
	inputs=dict(
		stringlist=List[String],
		seperator=String
		),
	output=dict(
		concatenated=String
		)
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
is an RExpression. This is most useful when connecting two R codes.

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

Create input and output ports using the flow.input and flow.output variables.

```python
flow.input.InputValue = List[Integer]
flow.output.OutputValue = List[Integer]
```

### Creating data links

Link ports using the >> operator. Output ports can be part of multiple links.
Input ports must only be linked once.

```python
flow.input.InputValue >> flow.task.MyTask.input.y
flow.task.MyTask.output.x >> flow.task.AnotherTask.input.x
flow.task.MyTask.output.x >> flow.output.OutputValue
```

For R scripts that contain variables with dots in the name, you can map them
from a valid Taverna name (no dots) to the R script name, using:

```python
flow.input.IsBeta >> flow.task.RCode.input.IsBeta['Is.Beta']
flow.task.RCode.output.ResultTable['result.table'] >> flow.output.ResultTable
```

### Shortcuts

For input and output ports, it is possible to assign a type and link to an activity
port using:

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

