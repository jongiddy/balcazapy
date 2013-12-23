# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

# This example creates a simple nested workflow. First, create the inner nested workflow:

# First, create your workflow

inner = Workflow(title='Projection Matrix')

# Create an input port. Note every port has a type. The type can be followed by
# additional information

inner.input.stageMatrix = RExpression(description="Stage matrix - an R matrix")

# Note, you may need to use a letter u in front of quotes for non-ASCII strings.

SpeciesName = String(
	description = u"""Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
""",
	example = "Gentiana pneumonanthe"
)

# Refer to workflow input ports using <wflow>.input.<portname>
# output ports usig <wflow>.output.<portname>

inner.input.speciesName = SpeciesName

rserve = RServer()

# Create a reusable activity and assign it to a workflow task, using
# <wflow>.task.<taskname> << <activity>
# 
# In this example, we create an RShell activity from a script and details of 
# the inputs and outputs. Note that the {} form and dict() form are similar, 
# but {} requires quotes, while dict() cannot handle names containing dots
#
# For RShell, if an R variable name is not a valid Taverna name (e.g. it 
# contains a dot) use inputMap to map the R variable name to a valid name

inner.task.CalculatePlotSize << rserve.code(
	"plot_size <- 128 + 32 * dim(stage.matrix)[1]",
	inputs = dict(stage_matrix = RExpression),
	outputs = dict(plot_size = Integer),
	inputMap = dict(stage_matrix='stage.matrix')
	)

# Task input ports are <wflow>.task.<taskname>.input.<portname>
# Connect ports using the | operator
# 

inner.input.stageMatrix | inner.task.CalculatePlotSize.input.stage_matrix

# Create another RShell, this time from an external R file

inner.task.ProjectionMatrix << rserve.file(
	"projectionMatrix.R",
	inputs=dict(plot_title=String, stage_matrix=RExpression, plot_size=Integer),
	outputs=dict(plot_image=PNG_Image)
	)
inner.task.ProjectionMatrix.description = 'Create a projection matrix'

# There is a handy shortcut for text constant inputs

inner.task.ProjectionMatrix.input.plot_title = "Projection Matrix"

inner.input.stageMatrix | inner.task.ProjectionMatrix.input.stage_matrix
inner.task.CalculatePlotSize.output.plot_size | inner.task.ProjectionMatrix.input.plot_size

inner.output.projectionMatrix = PNG_Image(description='Plot of results')

inner.task.ProjectionMatrix.output.plot_image | inner.output.projectionMatrix

# Create another workflow

flow = Workflow(title='Create Projection Matrix', author="Maria and Jon",
	description="Create a projection matrix from a stage matrix and a list of stages")

# and add the nested workflow (treat the nested workflow just like any other acivity)

flow.task.ProjectionMatrix << NestedWorkflow(inner)

# Hey, we can reuse our SpeciesName defined near the top of this file

flow.input.speciesName = SpeciesName

flow.input.stageMatrixFile = TextFile(
	description = """The stage matrix file input port:

Here comes the stage matrix without the stage names (as you see in the example).  It should be provied as a txt-file.  

Example from:
J. Gerard B. Oostermeijer; M.L. Brugman; E.R. de Boer; H.C.M. Den Nijs. 1996. Temporal and Spatial Variation in the Demography of Gentiana pneumonanthe, a Rare Perennial Herb. The Journal of Ecology, Vol. 84(2): 153-166.
""",
	example = """0.0000	0.0000	0.0000	7.6660	0.0000
0.0579	0.0100	0.0000	8.5238	0.0000
0.4637	0.8300	0.9009	0.2857	0.8604
0.0000	0.0400	0.0090	0.6190	0.1162
0.0000	0.0300	0.0180	0.0000	0.0232"""
)

# List types must identify what the list contains

flow.input.stages = List[String]


rshell = rserve.file(
	"readMatrix.R",
	inputs = dict(stage_matrix_file=TextFile, stages=Vector[String]),
	outputs = dict(stage_matrix=RExpression)
	)

flow.task.ReadMatrix << rshell

flow.input.stageMatrixFile | flow.task.ReadMatrix.input.stage_matrix_file
flow.input.stages | flow.task.ReadMatrix.input.stages

flow.task.ReadMatrix.output.stage_matrix | flow.task.ProjectionMatrix.input.stageMatrix # not inner.input.stageMatrix !
flow.input.speciesName | flow.task.ProjectionMatrix.input.speciesName

flow.output.projectionMatrix = PNG_Image(description = "A projection matrix")

flow.task.ProjectionMatrix.output.projectionMatrix | flow.output.projectionMatrix
