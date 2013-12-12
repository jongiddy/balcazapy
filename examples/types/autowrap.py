# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *
from balcaza.t2wrapper import WrapperWorkflow

# This example creates a simple nested workflow. First, create the flow nested workflow:

flow = Workflow(title='Projection Matrix')


flow.task.Process = BeanshellCode("output = input1 + input2;",
	inputs=dict(
		input1=String['YES', 'NO'](description="Choose YES or NO", example="YES"),
		input2=Logical),
	outputs=dict(output=String))
	
flow.input.Choice = flow.task.Process.input.input1
flow.input.Logicals = List[Logical]
flow.input.Logicals >> flow.task.Process.input.input2
flow.output.Output = List[String]
flow.task.Process.output.output >> flow.output.Output

flow = WrapperWorkflow(flow)
