# Balcazapy
Create a Taverna workflow file (t2flow format) using a script.

## Installation

### Linux

1.  Ensure Python 2.7 and Git are installed, preferably using your system's
    package manager.

2.  Go to http://github.com/jongiddy/balcazapy and copy the HTTPS clone 
    URL on the right to the clipboard.

    Click on the clipboard-arrow icon to copy the URL to the clipboard

3.  Clone the Git repository, using the copied URL

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

4.  Run:

    ```
    $ cd balcazapy
    $ ./setup.sh
    ```

This installs a command `balc` into the `bin` directory. Add the `bin` directory
to your `PATH`, copy the `balc` executable to somewhere in your `PATH`, or 
reference `balc` with an absolute path name.

### Windows

1.  Install Python 2.7 from http://www.python.org/

    Python 3 is also available. Balcazapy does not yet work with Python 3.
    
    On Windows, use the appropriate 32-bit or 64-bit MSI Installer. Use 
    **Control Panel -> System and Security -> System** to check whether your 
    Windows version is 32-bit or 64-bit. You do not need the MSI program database.
    
    Use the default values for installation.

2.  Install Git from http://git-scm.com/

    Use the default values for installation, *EXCEPT* for the page titled 
    **Adjusting your PATH environment**, where you should select 
    **Run Git from the Windows Command Prompt**

3.  Go to http://github.com/jongiddy/balcazapy and copy the HTTPS clone 
    URL on the right to the clipboard.

    Click on the clipboard-arrow icon to copy the URL to the clipboard

4.  Open a command window (**Start menu -> Accessories -> Command Prompt**).

5.  Clone the Git repository, using the copied URL (right click to paste into the command window)

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

6.  Check the file locations in `setup.bat`, then run:

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
usage: balc [-h] [--indent] [--validate] [--flow FLOWNAME] source [target]

Create a Taverna 2 workflow (t2flow) file from a Zapy description file

positional arguments:
  source           Zapy (.py) description file
  target           Taverna 2 Workflow (.t2flow) filename (default: stdout)

optional arguments:
  -h, --help       show this help message and exit
  --indent         create a larger but more readable indented file
  --validate       modify workflow to validate input ports
  --flow FLOWNAME  name of the workflow in the source file (default: flow)
```

## Creating a Zapy Description File
Zapy files are Python files. Hence, they have a .py suffix. Using the Python
format allows Zapy files to be edited in highlighting editors, including Idle, 
the editor that comes with Python.

### Prologue
Python requires that (almost) all names used, but not defined, in a file are 
imported from libraries. To make use of Balcazapy, start with these lines:

```python
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow
```

### Workflows

Create a workflow using:

```python
flow = Workflow(title = 'Create Projection Matrix', author = "Maria and Jon",
    description = "Create a projection matrix from a stage matrix and a list of stages")
```

This workflow contains 3 main collections:

- `flow.input` - the input ports for the workflow

- `flow.output` - the output ports for the workflow

- `flow.task` - the connected tasks within the workflow

### Tasks

Tasks are created by passing an *Activity* to a workflow task name.  The 
available activities are described below.

```python
flow.task.MyTask << rserve.code(
    'total <- sum(vals)',
    inputs = dict(
        vals = Vector[Integer]
        ),
    outputs = dict(
        total = Integer
        )
    )
```

Each task contains 2 collections:

- `flow.task.MyTask.input` - the input ports for the task

- `flow.task.MyTask.output` - the output ports for the task

Manage task parallelisation and retries using:

```python
flow.task.MyTask.parallel(maxJobs = 5)
flow.task.MyTask.retry(maxRetries = 3, initialDelay = 1000, maxDelay = 5000,
    backoffFactor = 1.0)
```

### Data Links

Link ports using the `|` (pipe) symbol. Output ports can be part of multiple
links. Input ports must only be linked once.

```python
flow.input.InputValues | flow.task.MyTask.input.vals
flow.task.MyTask.output.total | flow.task.AnotherTask.input.x
flow.task.MyTask.output.total | flow.output.SumOfValues
```

It is possible to create a chain when a task has default input and output ports.

```
flow.task.MyTask << rserve.code(
    'total <- sum(vals)',
    inputs = dict(vals = Vector[Integer]),
    outputs = dict(total = Integer),
    defaultInput = 'vals',
    defaultOutput = 'total'
    )
flow.input.InputValues | flow.task.MyTask | flow.output.SumOfValues
```

To iterate a task for all values in a List, add `+` to the pipe before the port
to be iterated and `-` for the port that collects the multiple results.

```python
flow.input.ListOfStrings |+ flow.task.ProcessSingleString |- flow.output.ProcessedStrings
flow.input.ListOfListsOfStrings |++ flow.task.ProcessSingleString |-- flow.output.MoreProcessedStrings
```

### Control Links

Force services to run in sequence using the `>>` operator between tasks:

```python
flow.task.MyTask >> flow.task.AnotherTask
```

### Activities

Activities are the boxes you see in a workflow. Activities describe a particular 
task to be performed. There are several types of activities.

Activities can be created and assigned to named workflow tasks.

Activities can be reused, by assigning them to multiple tasks.

In pipelines, it is possible to use activities in place of tasks, and a task
will be created. This is very useful for reuse of simple activities in
pipelines.

```python
SumValues = rserve.code(
    'total <- sum(vals)',
    inputs = dict(vals = Vector[Integer]),
    outputs = dict(total = Integer),
    defaultInput = 'vals',
    defaultOutput = 'total'
    )
flow.input.ListOfListsOfValues |+ SumValues |- SumValues | flow.output.GrandTotal
```

In this example, the first `SumValues` activity processes each outer list, to 
create a list of totals, and the second `SumValues` activity sums these totals 
to create a grand total.

#### Types

For some activities, you will need to specify a 
type for a port.

Available types are:

- `Integer`
- `Number`
- `String`
- `TextFile`
- `PDF_File`
- `PNG_Image`

For interaction with R code, the following additional types are available:

- `Logical`
- `RExpression`
- `Vector[Logical]`
- `Vector[Integer]`
- `Vector[Number]`
- `Vector[String]`

You can also specify lists using `List[type]`, where `type` is any of the above,
or another list. For example:

- `List[Integer]` - a list of integers
- `List[RExpression]` - a list of RExpressions
- `List[List[String]]` - a list containing lists of strings

String types can be restricted to a set of values, and Integer types to a
range, using:

```python
String['YES', 'NO']
Integer[0,...,100]
```

The `--validate` option to `balc` will add additional checks that input values
have the correct type.

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
    inputs = dict(
        stringlist = List[String],
        seperator = String
        ),
    output = dict(
        concatenated = String
        )
    )
```

or

```python
BeanshellFile(
    'file.bsh',
    inputs = dict(
        stringlist = List[String],
        seperator = String
        ),
    output = dict(
        concatenated = String
        )
    )
```

All inputs and outputs for BeanShell are strings or lists of strings. However,
it is possible to pass other types, for documentation purposes. Just remember
that the Beanshell will see a String or a List type internally.

#### Interaction Pages

Create using:

```python
InteractionPage(url,
    inputs = dict(
        start = Integer,
        end = Integer
        ),
    outputs = dict(
        sequences = List[List[Integer]]
        )
    )
```

#### HTTP (REST) Calls

Create using:

```python
HTTP.GET('http://www.biovel.eu/')
HTTP.PUT(
    'http://balca.biovel.eu/openacces/{file_name}',
    inputs = dict(
        file_name = String
        ),
    escapeParameters = False
    )
```

For HTTP calls, the default input is the body of the HTTP request, and the 
default output is the body of the HTTP response.

#### Text Constant
Create using:

```python
TextConstant('Some text')
```

For text constants, the default output is the text value.

#### R Scripts

For R scripts, first create an RServer using

```python
rserve = RServer(host, port)
```

If the port is omitted, the default Rserve port (6311) will be used.

If the host is omitted, localhost will be used.

Create an R activity using

```python
rserve.code(
    'total <- sum(vals)',
    inputs = dict(
        vals = Vector[Integer]
        ),
    outputs = dict(
        total = Integer
        )
    )
```

or

```python
rserve.file(
    'file.r',
    inputs = dict(
        vals = Vector[Integer]
        ),
    outputs = dict(
        total = Integer
        )
    )
```

For R scripts that contain variables with dots in the name, you can map them
from a valid Taverna name (no dots) to the R script name, using:

```python
rserve.file(
    'file.r',
    inputs = dict(IsBeta = Logical),
    inputMap = dict(IsBeta = 'Is.Beta'),
    outputs = dict(ResultTable = RExpression),
    outputMap = dict(ResultTable = 'result.table')
    )
```

This can also be used to output results as multiple types:
```python
rserve.code(
    'total <- sum(vals)',
    outputs = dict(
        total = RExpression,
        totalAsInt = Integer,
        totalAsVector = Vector[Integer]
        ),
    outputMap = dict(
        totalAsInt = total,
        totalAsVector = total
        )
    )
```

Note that the List type is not available for RServer activity ports.  Use the 
Vector type instead.

For R scripts, the default input and output is the R workspace

#### XPath

Create using:

```python
XPath('/Job/JobId')
XPath('/xhtml:html/xhtml:head/xhtml:title', {'xhtml': 'http://www.w3.org/1999/xhtml'})
```

For XPath, the default input is the XPath expression, and the default output is
a list of matched text elements.

### Nested Workflows

It is possible to create nested workflows using the NestedWorkflow activity.

```python
inner = Workflow(...)
...
outer = Workflow(...)
outer.task.CoreAlgorithm << NestedWorkflow(inner)
```

It is often more convenient to develop the nested workflow in a separate file,
and then use:

```python
outer.task.CoreAlgorithm << NestedZapyFile('inner.py')
```

### Shortcuts

For input and output ports, it is possible to assign a type and link to an activity
port using:

```python
flow.input.InputValues | flow.task.MyTask.input.vals
flow.task.MyTask.output.x | flow.output.OutputValue
```

The types are inferred from the activity types (e.g. an R Vector becomes a List).

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
flow.task.MyTask.input.plot_title = "Initial Results"
```

To make access to task ports less verbose, assign the task to a variable:

```python
MyTask = flow.task.MyTask << rserve.code(...)
flow.input.values = MyTask.input.vals
MyTask.output.total | AnotherTask.input.in1
```

You do not need to specify input or output ports for RExpression types in RServe
activities. This is most useful when connecting two RServe activities, as shown
in the following complete example:

```python
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title = 'TwiceTheSum')

rserve = RServer()

SumValues = flow.task.SumValues << rserve.code(
    'total <- sum(vals)',
    inputs = dict(vals = Vector[Integer[0,...,100]])
    )
Double = flow.task.Double << rserve.code(
    'out1 <- 2 * in1',
    outputs = dict(out1 = Integer)
    )

# Link internal script variables (transferred as RExpression types)
SumValues.output.total | Double.input.in1

SumValues.extendUnusedInputs()
Double.extendUnusedOutputs()
```

Tasks and activities can be chained using their default input and output ports.
See examples/rest/web.py for an example.

### Annotations

Workflow annotations are defined during creation, but can be overridden:

```python
flow = Workflow(title = 'Create Projection Matrix', author = "Maria and Jon",
    description = "Create a projection matrix from a stage matrix and a list of stages")
flow.title = 'Create Projection Matrix v1'
```

A task annotation can come from an activity, but can be overridden:

```python
flow.task.MyTask = HTTP.GET(url, description="Fetch the page")
flow.task.MyTask.description = "Fetch a page" # override above
```

Port annotations can come from the type, but can be overridden

```python
flow.input.Location = String(description="The site name", example="Terschelling")
flow.input.Location.example = "Dwingeloo"
```
