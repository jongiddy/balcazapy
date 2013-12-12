# -*- coding: utf-8 -*-
### Do not edit the lines at the top and bottom of this file.
### Edit the workflow description between START and FINISH comments
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

### START editing your workflow below here

flow = Workflow(title='Projection Matrix')

# Create a reusable port type

SpeciesName = String(
	description = """Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
""",
	example = "Gentiana pneumonanthe"
)

# Refer to workflow input ports using <wflow>.input.<portname>
# output ports usig <wflow>.output.<portname>

flow.input.speciesName = SpeciesName
flow.input.stageMatrix = RExpression

rserve = RServer()

# Create a reusable activity and assign it to a workflow task, using
# <wflow>.task.<taskname> = <activity>
# 
# In this example, we create an RShell activity from a script and details of 
# the inputs and outputs. Note that the {} form and dict() form are similar, 
# but {} requires quotes, while dict() cannot handle names containing dots

flow.task.CalculatePlotSize = rserve.code(
	"plot_size <- 128 + 32 * dim(stage.matrix)[1]",
	inputs = {'stage.matrix': RExpression},
	outputs = dict(plot_size = Integer)
	)

# Task input ports are <wflow>.task.<taskname>.input.<portname>
# Connect ports using the >> operator
# 
# For RShell, if an R variable name is not a valid Taverna name (e.g. it contains a dot)
# use [] to provide the R variable name after the Taverna name

flow.input.stageMatrix >> flow.task.CalculatePlotSize.input.stage_matrix['stage.matrix']

# Create another RShell, this time from an external R file

flow.task.ProjectionMatrix = rserve.file(
	"projectionMatrix.R",
	inputs=dict(plot_title=String, stage_matrix=RExpression, plot_size=Integer),
	outputs=dict(plot_image=PNG_Image)
	)
flow.task.ProjectionMatrix.description = 'Create a projection matrix'

# There is a handy shortcut for text constant inputs

"Projection Matrix" >> flow.task.ProjectionMatrix.input.plot_title

flow.input.stageMatrix >> flow.task.ProjectionMatrix.input.stage_matrix
flow.task.CalculatePlotSize.output.plot_size >> flow.task.ProjectionMatrix.input.plot_size

flow.output.projectionMatrix = PNG_Image(description='Plot of results')

flow.task.ProjectionMatrix.output.plot_image >> flow.output.projectionMatrix


# Set compressed = True to create a smaller workflow file
# Set compressed = False to create a workflow indented for readability

compressed = True

# FINISH your workflow above here, and do not change the lines below

if __name__ == '__main__':
	import codecs, sys
	import maximal.XMLExport as XMLExport

	UTF8Writer = codecs.getwriter('utf8')
	stdout = UTF8Writer(sys.stdout)

	if compressed:
		flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLCompressor(stdout)))
	else:
		flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(stdout)))
