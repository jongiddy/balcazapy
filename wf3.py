

from t2types import *
from t2activity import *
from t2flow import *


w1 = Workflow('eigen analysis')

desc = """Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
"""

example = "Gentiana pneumonanthe"

speciesName = w1.addInput('speciesName', String, desc, example)

desc = """The stage matrix file input port:

Here comes the stage matrix without the stage names (as you see in the example).  It should be provied as a txt-file.  

Example from:
J. Gerard B. Oostermeijer; M.L. Brugman; E.R. de Boer; H.C.M. Den Nijs. 1996. Temporal and Spatial Variation in the Demography of Gentiana pneumonanthe, a Rare Perennial Herb. The Journal of Ecology, Vol. 84(2): 153-166.
"""

example = """0.0000	0.0000	0.0000	7.6660	0.0000
0.0579	0.0100	0.0000	8.5238	0.0000
0.4637	0.8300	0.9009	0.2857	0.8604
0.0000	0.0400	0.0090	0.6190	0.1162
0.0000	0.0300	0.0180	0.0000	0.0232"""

stageMatrix = w1.addInput('stageMatrix', RExpression, desc, example)

rserve = RServer()

rshell = rserve.script("plot_size <- 128 + 32 * dim(stage_matrix)[1]")
rshell.input(stage_matrix=RExpression).output(plot_size=Integer)

plotSize = w1.addTask("CalculatePlotSize", rshell)

w1.linkData(stageMatrix, plotSize.input.stage_matrix)

with open("projectionMatrix.R") as f:
    rshell = rserve.script(f.read())
rshell.input(plot_title=String, stage_matrix=RExpression, plot_size=Integer).output(plot_image=PNGImage)

projMatrix = w1.addTask("ProjectionMatrix", rshell, "Create a projection matrix")

w1.linkData("Projection Matrix", projMatrix.input.plot_title)
w1.linkData(stageMatrix, projMatrix.input.stage_matrix)
w1.linkData(plotSize.output.plot_size, projMatrix.input.plot_size)

graph = w1.addOutput('projectionMatrix', PNGImage, 'Plot of results')

w1.linkData(projMatrix.output.plot_image, graph)

w2 = Workflow('Eigen analysis')

nested = w2.addFlow('Eigen analysis', w1)

desc = """Species name

Controls the title of the bar plot that will be generated with the analysis. As an example, it can be the name of the species or the name of the place where the research has been conducted, between others.
"""

example = "Gentiana pneumonanthe"

speciesName = w2.addInput('speciesName', String, desc, example)



stageMatrixFile = w2.addInput('stageMatrixFile', String)

stages = w2.addInput('stages', List(String))


with open("readMatrix.R") as f:
    rshell = rserve.script(f.read())
rshell.input(stage_matrix_file=String, stages=Vector(String)).output(stage_matrix=RExpression)

readMatrix = w2.addTask('ReadMatrix', rshell)

w2.linkData(stageMatrixFile, readMatrix.input.stage_matrix_file)
w2.linkData(stages, readMatrix.input.stages)

# w2.linkData(readMatrix.output.stage_matrix, nested.input.stageMatrix)
# w2.linkData(speciesName, nested.input.speciesName)

projMatrix = w2.addOutput('projectionMatrix', PNGImage)

w2.linkData(nested.output.projectionMatrix, projMatrix)

w2.setAuthors(Annotation('Maria and Jon'))
w2.setDescription(Annotation('Hello'))
w2.setTitle(Annotation('Workflow 34'))

import sys, XMLExport
w2.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(sys.stdout)))


