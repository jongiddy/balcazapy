# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

# This example demonstrates validation checks of input ports
# Create the t2flow file using the --validate option

flow = Workflow(title='Validation Example')


flow.task.Process << BeanshellCode("output = input1 + input2;",
	inputs=dict(
		input1=String['YES', 'NO'](description="Choose YES or NO", example="YES"),
		input2=Logical(description="Choose TRUE or FALSE", example="TRUE")
		),
	outputs=dict(output=String))
	
flow.input.Choice = flow.task.Process.input.input1
# Note, as we are changing the depth of the input, we need to redo the annotations
flow.input.Logicals = List[Logical](description="Choose TRUE or FALSE", example="TRUE")
flow.input.Logicals | flow.task.Process.input.input2
flow.output.Output = List[String]
flow.task.Process.output.output | flow.output.Output
