# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

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
# <wflow>.task.<taskname> << <activity>
# 
# In this example, we create an RShell activity from a script and details of 
# the inputs and outputs. Note that the {} form and dict() form are similar, 
# but {} requires quotes, while dict() cannot handle names containing dots

flow.task.CalculatePlotSize << rserve.code(
	"plot_size <- 128 + 32 * dim(stage.matrix)[1]",
	outputs = dict(plot_size = Integer)
	)

# Task input ports are <wflow>.task.<taskname>.input.<portname>
# Connect ports using the >> operator
# 
# For RShell, if an R variable name is not a valid Taverna name (e.g. it contains a dot)
# use [] to provide the R variable name after the Taverna name
#
# Note that RExpression inputs and outputs do not need to be specified as inputs
# or outputs above.

flow.input.stageMatrix >> flow.task.CalculatePlotSize.input.stage_matrix['stage.matrix']

# Create another RShell, this time from an external R file

flow.task.ProjectionMatrix << rserve.file(
	"projectionMatrix.R",
	inputs=dict(plot_title=String, plot_size=Integer),
	outputs=dict(plot_image=PNG_Image)
	)
flow.task.ProjectionMatrix.description = 'Create a projection matrix'

# There is a handy shortcut for text constant inputs

"Projection Matrix" >> flow.task.ProjectionMatrix.input.plot_title

flow.input.stageMatrix >> flow.task.ProjectionMatrix.input.stage_matrix
flow.task.CalculatePlotSize.output.plot_size >> flow.task.ProjectionMatrix.input.plot_size

flow.output.projectionMatrix = PNG_Image(description='Plot of results')

flow.task.ProjectionMatrix.output.plot_image >> flow.output.projectionMatrix

# Create a nested workflow that can be imported into other workflows

ProjectionMatrix = NestedWorkflow(flow)
