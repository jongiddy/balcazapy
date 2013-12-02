from t2types import *
from t2activity import *
from t2flow import *

w1 = Workflow('eigenanalysis')

w1.input.speciesName = String
w1.input.speciesName.description = """Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
"""
w1.input.speciesName.example = "Gentiana pneumonanthe"


w1.input.stageMatrix = RExpression

rserve = RServer()

w1.task.CalculatePlotSize = rserve.runScript(
	"plot_size <- 128 + 32 * dim(stage_matrix)[1]",
	inputs = dict(stage_matrix=RExpression),
	outputs = dict(plot_size=Integer)
	)

w1.input.stageMatrix >> w1.task.CalculatePlotSize.input.stage_matrix

w1.task.ProjectionMatrix = rserve.runFile(
	"projectionMatrix.R",
	inputs=dict(plot_title=String, stage_matrix=RExpression, plot_size=Integer),
	outputs=dict(plot_image=PNGImage)
	)
w1.task.ProjectionMatrix.description = 'Create a projection matrix'

"Projection Matrix" >> w1.task.ProjectionMatrix.input.plot_title

w1.input.stageMatrix >> w1.task.ProjectionMatrix.input.stage_matrix
w1.task.CalculatePlotSize.output.plot_size >> w1.task.ProjectionMatrix.input.plot_size

w1.output.projectionMatrix = PNGImage
w1.output.projectionMatrix.description = 'Plot of results'

w1.task.ProjectionMatrix.output.plot_image >> w1.output.projectionMatrix

w2 = Workflow('Eigenanalysis')

w2.task.Eigenanalysis = w1

desc = """Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
"""

example = "Gentiana pneumonanthe"

w2.input.speciesName = String
sn = w2.input.speciesName
sn.description = desc
sn.example = example


w2.input.stageMatrixFile = TextFile
w2.input.stageMatrixFile.description = """The stage matrix file input port:

Here comes the stage matrix without the stage names (as you see in the example).  It should be provied as a txt-file.  

Example from:
J. Gerard B. Oostermeijer; M.L. Brugman; E.R. de Boer; H.C.M. Den Nijs. 1996. Temporal and Spatial Variation in the Demography of Gentiana pneumonanthe, a Rare Perennial Herb. The Journal of Ecology, Vol. 84(2): 153-166.
"""
w2.input.stageMatrixFile.example = """0.0000	0.0000	0.0000	7.6660	0.0000
0.0579	0.0100	0.0000	8.5238	0.0000
0.4637	0.8300	0.9009	0.2857	0.8604
0.0000	0.0400	0.0090	0.6190	0.1162
0.0000	0.0300	0.0180	0.0000	0.0232"""

w2.input.stages = List(String)


rshell = rserve.runFile(
	"readMatrix.R",
	inputs = dict(stage_matrix_file=TextFile, stages=Vector(String)),
	outputs = dict(stage_matrix=RExpression)
	)

w2.task.ReadMatrix = rshell

w2.input.stageMatrixFile >> w2.task.ReadMatrix.input.stage_matrix_file
w2.input.stages >> w2.task.ReadMatrix.input.stages

w2.task.ReadMatrix.output.stage_matrix >> w2.task.Eigenanalysis.input.stageMatrix # not w1.input.stageMatrix !
w2.input.speciesName >> w2.task.Eigenanalysis.input.speciesName

w2.output.projectionMatrix = PNGImage

w2.task.Eigenanalysis.output.projectionMatrix >> w2.output.projectionMatrix

w2.author = 'Maria and Jon'
w2.description = 'Hello'
w2.title = 'Workflow 34'

import sys, XMLExport
w2.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(sys.stdout)))


