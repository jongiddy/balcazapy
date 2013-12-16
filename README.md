# Balcazapy
Create a Taverna workflow file (t2flow format) using a script.

## Installation

### Linux

1.	Ensure Python 2.7 and Git are installed, preferbaly using your system's
	package manager.

2.	Go to http://github.com/jongiddy/balcazapy and copy the HTTPS clone 
	URL on the right to the clipboard.

	Click on the clipboard-arrow icon to copy the URL to the clipboard

3.	Clone the Git repository, using the copied URL

	```
	$ git clone https://github.com/jongiddy/balcazapy.git
	```

	Note, this creates a folder called `balcazapy`

	If you have already cloned the repository, you can update to the latest
	version using the command:

	```
	$ cd balcazpy
	$ git pull
	```

4.	Run:

	```
	$ cd balcazapy
	$ ./setup.sh
	```

This installs a command `balc` into the `bin` directory. Add the `bin` directory
to your `PATH`, copy the `balc` executable to somewhere in your `PATH`, or 
reference `balc` with an absolute path name.

### Windows

1.	Install Python 2.7 from http://www.python.org/

	Python 3 is also available. Balcazapy does not yet work with Python 3.
	
	On Windows, use the appropriate 32-bit or 64-bit MSI Installer. Use 
	**Control Panel -> System and Security -> System** to check whether your 
	Windows version is 32-bit or 64-bit. You do not need the MSI program database.
	
	Use the default values for installation.

2.	Install Git from http://git-scm.com/

	Use the default values for installation, *EXCEPT* for the page titled 
	**Adjusting your PATH environment**, where you should select 
	**Run Git from the Windows Command Prompt**

3.	Go to http://github.com/jongiddy/balcazapy and copy the HTTPS clone 
	URL on the right to the clipboard.

	Click on the clipboard-arrow icon to copy the URL to the clipboard

4.	Open a command window (**Start menu -> Accessories -> Command Prompt**).

5.	Clone the Git repository, using the copied URL (right click to paste into the command window)

	```
	> git clone https://github.com/jongiddy/balcazapy.git
	```

	Note, this creates a folder called `balcazapy`

	If you have already cloned the repository, you can update to the latest
	version using the command:

	```
	> cd balcazapy
	> git pull
	```

6.	Check the file locations in `setup.bat`, then run:

	```
	> cd balcazapy
	> setup.bat
	```

This installs a batch script `balc.bat` into the `bin` folder. Add the `bin` 
folder to your `PATH`, copy the `balc.bat` script to somewhere in your `PATH`, 
or reference `balc.bat` with an absolute path name.

## Creating a Taverna 2 Workflow (t2flow) file

The `balc` command converts a Zapy description file to a Taverna t2flow file.

To create a t2flow file from an existing Zapy description file, run the command:

```
balc myfile.py myflow.t2flow
```

Run `balc -h` to see the available options:

```
usage: balc [-h] [--indent] [--flow FLOWNAME] source [target]

Create a Taverna 2 workflow (t2flow) file from a Python script

positional arguments:
  source           Python source filename
  target           Taverna 2 Workflow (t2flow) filename (default: stdout)

optional arguments:
  -h, --help       show this help message and exit
  --indent         create a larger but more readable indented file
  --flow FLOWNAME  name of the workflow in the source file (default: flow)
```

## Creating a Zapy Description File
Zapy files are Python files. Hence, they have a .py suffix. Using the Python
format allows Zapy files to be edited in highlighting editors, including Idle, 
the editor that comes with Python.

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

This workflow contains 3 main collections:

- `flow.input` - the input ports for the workflow

- `flow.output` - the output ports for the workflow

- `flow.task` - the connected tasks within the workflow

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

### Input and output ports

Create input and output ports using the `flow.input` and `flow.output` 
collections.  Assign a port type to a port name, as shown:

```python
flow.input.InputValues = List[Integer]
flow.output.OutputValue = Integer
```
### Tasks

Tasks are created similarly to input and output ports, but instead of being
assigned a type, they are assigned an *Activity*.  The available activities are
described below.

```python
flow.task.MyTask = rserve.code(
	'x <- y',
	inputs=dict(y=Vector[Integer]),
	outputs=dict(x=Vector[Integer])
	)
```

Each task contains 2 collections:

- `flow.task.MyTask.input` - the input ports for the task

- `flow.task.MyTask.output` - the output ports for the task


### Creating data links

Link ports using the `>>` operator. Output ports can be part of multiple links.
Input ports must only be linked once.

```python
flow.input.InputValue >> flow.task.MyTask.input.y
flow.task.MyTask.output.x >> flow.task.AnotherTask.input.x
flow.task.MyTask.output.x >> flow.output.OutputValue
```

### Activities

Activities are the boxes you see in a workflow. Activities describe a particular 
task to be performed. There are several types of activities.

Activities can be created and assigned to named workflow tasks.

Activities can be reused, by assigning them to multiple tasks.

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
InteractionPage(url,
	inputs=dict(
		start=Integer,
		end=Integer
		),
	outputs=dict(
		sequences=List[List[Integer]]
		)
	)
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

For R scripts that contain variables with dots in the name, you can map them
from a valid Taverna name (no dots) to the R script name, using:

```python
flow.input.IsBeta >> flow.task.RCode.input.IsBeta['Is.Beta']
flow.task.RCode.output.ResultTable['result.table'] >> flow.output.ResultTable
```

### Nested Workflows

It is possible to create nested workflows using the NestedWorkflow activity.

```python
inner = Workflow(...)
...
outer = Workflow(...)
outer.task.CoreAlgorithm = NestedWorkflow(inner)
```

It is often more convenient to develop the nested workflow in a separate file,
and then use:

```python
outer.task.CoreAlgorithm = NestedZapyFile('inner.py')
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

Text constants can be created and linked in one step using:

```python
"Initial Results" >> flow.task.MyTask.input.plot_title
```