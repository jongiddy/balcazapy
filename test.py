

from t2types import *
from t2activity import *
from t2flow import *


wflow = Workflow('test')
years = wflow.addInput('years', List(Integer), 'Number of years') # returns a sender

rserve = RServer('localhost', 3619)

with open("simple.R") as f:
    rshell = rserve.Task(script=f.read(), inputs = {'foo': Vector(Integer)}, outputs = {'graph': PNGImage})

r2 = wflow.addTask("DoStuff", rshell, "Do some R stuff") # returns r1

wflow.linkData(years, r2.input.foo) # sender, receiver, check they are compatible

graph = wflow.addOutput('graph', PNGImage, 'Plot of results')

wflow.linkData(r2.output.graph, graph)



bigwflow = Workflow('big')
r3 = bigwflow.addFlow('LTRE', wflow)

years = bigwflow.addInput('years', List(Integer))
bigwflow.linkData(years, r3.input.years)

bigwflow.setAuthors(Annotation('Maria and Jon'))
bigwflow.setDescription(Annotation('Hello'))
bigwflow.setTitle(Annotation('Workflow 34'))

import sys, XMLExport
bigwflow.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(sys.stdout)))


# f = Workflow.Taverna2FlowSourceFile("file")
# wflow = f.read()

# years = wflow.getInput("years")
# rshell = wflow.getTask("DoStuff")
# graph = wflow.getOutput("graph")
# link = wflow.getMaybeLink(rshell.output.graph, graph) # return None if not existsa
# wflow.deleteLink(link)

# wflow.getInputs() # {'name': type}