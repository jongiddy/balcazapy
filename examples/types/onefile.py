# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

# This example creates a simple nested workflow. First, create the flow nested workflow:

flow = Workflow(title='Projection Matrix')


flow.task.Process = BeanshellCode("output = input1 + input2;",
	inputs=dict(input1=String['YES', 'NO'], input2=Logical),
	outputs=dict(output=String))

flow.input.Choice = String(description="Choose YES or NO", example="YES")
flow.input.Logical = String
	
flow.input.Choice >> flow.task.Process.input.input1
flow.input.Logical >> flow.task.Process.input.input2
flow.output.Output = flow.task.Process.output.output

