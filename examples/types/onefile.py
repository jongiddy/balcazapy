# -*- coding: utf-8 -*-
### Do not edit the lines at the top and bottom of this file.
### Edit the workflow description between START and FINISH comments
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

### START editing your workflow below here
#
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

# Set compressed = True to create a smaller workflow file
# Set compressed = False to create a workflow indented for readability

compressed = True

# FINISH your workflow above here, and do not change the lines below

import codecs, sys
import maximal.XMLExport as XMLExport

UTF8Writer = codecs.getwriter('utf8')
stdout = UTF8Writer(sys.stdout)

if compressed:
	flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLCompressor(stdout)))
else:
	flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(stdout)))

