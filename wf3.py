### Do not edit the lines at the top and bottom of this file.
### Edit the workflow description between START and FINISH comments
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

### START editing your workflow below here
#
# This example creates a simple nested workflow. First, create the inner nested workflow:

inner = Workflow(title='Projection Matrix')

# Create a reusable port type

SpeciesName = String(
	description = """Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
""",
	example = "Gentiana pneumonanthe"
)

# Refer to workflow input ports using <wflow>.input.<portname>
# output ports usig <wflow>.output.<portname>

inner.input.speciesName = SpeciesName

inner.input.stageMatrix = RExpression

rserve = RServer()

# Create a reusable activity and assign it to a workflow task, using
# <wflow>.task.<taskname> = <activity>

inner.task.CalculatePlotSize = rserve.runScript(
	"plot_size <- 128 + 32 * dim(stage_matrix)[1]",
	inputs = dict(stage_matrix=RExpression),
	outputs = dict(plot_size=Integer)
	)

# Task input ports are <wflow>.task.<taskname>.input.<portname>
# Connect ports using the >> operator

inner.input.stageMatrix >> inner.task.CalculatePlotSize.input.stage_matrix

inner.task.ProjectionMatrix = rserve.runFile(
	"projectionMatrix.R",
	inputs=dict(plot_title=String, stage_matrix=RExpression, plot_size=Integer),
	outputs=dict(plot_image=PNGImage)
	)
inner.task.ProjectionMatrix.description = 'Create a projection matrix'

# There is a handy shortcut for text constant inputs

"Projection Matrix" >> inner.task.ProjectionMatrix.input.plot_title

inner.input.stageMatrix >> inner.task.ProjectionMatrix.input.stage_matrix
inner.task.CalculatePlotSize.output.plot_size >> inner.task.ProjectionMatrix.input.plot_size

inner.output.projectionMatrix = PNGImage(description='Plot of results')

inner.task.ProjectionMatrix.output.plot_image >> inner.output.projectionMatrix

# Create another workflow

outer = Workflow(title='Create Projection Matrix', author="Maria and Jon",
	description="Create a projection matrix from a stage matrix and a list of stages")

# and add the nested workflow (treat the nested workflow just like any other acivity)

outer.task.ProjectionMatrix = inner

# Hey, we can reuse our SpeciesName defined near the top of this file

outer.input.speciesName = SpeciesName


outer.input.stageMatrixFile = TextFile(
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

outer.input.stages = List[String]


rshell = rserve.runFile(
	"readMatrix.R",
	inputs = dict(stage_matrix_file=TextFile, stages=Vector[String]),
	outputs = dict(stage_matrix=RExpression)
	)

outer.task.ReadMatrix = rshell

outer.input.stageMatrixFile >> outer.task.ReadMatrix.input.stage_matrix_file
outer.input.stages >> outer.task.ReadMatrix.input.stages

outer.task.ReadMatrix.output.stage_matrix >> outer.task.ProjectionMatrix.input.stageMatrix # not inner.input.stageMatrix !
outer.input.speciesName >> outer.task.ProjectionMatrix.input.speciesName

outer.output.projectionMatrix = PNGImage(description = "A projection matrix")

outer.task.ProjectionMatrix.output.projectionMatrix >> outer.output.projectionMatrix


# Set compressed = True to create a smaller workflow file
# Set compressed = False to create a workflow indented for readability

compressed = True

# FINISH your workflow above here, and do not change the lines below

import sys
import maximal.XMLExport as XMLExport

if compressed:
	outer.exportXML(XMLExport.XMLExporter(XMLExport.XMLCompressor(sys.stdout)))
else:
	outer.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(sys.stdout)))

