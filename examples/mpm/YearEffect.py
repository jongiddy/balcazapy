# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title='Year Effect', author=u'Maria Paula Balcázar-Vargas, Jonathan Giddy and Gerard Oostermeijer')

flow.input.years = List[Integer[1500,...,2100]](
	description="All years which start a period of transition. This is likely to be all the years in which a survey was performed, apart from the last yearself.",
	example="[1987, 1988, 1989, 1990, 1991, 1992]"
	)

flow.input.stages = List[String](
	description='''Growth stages of the species populations

The names of the stages or categories of the input matrix.

In the following example, the matrix has 5 stages or categories:

	S	J	V	G	D
S	0.0000	0.0000	0.0000	7.6660	0.0000
J	0.0579	0.0100	0.0000	8.5238	0.0000
V	0.4637	0.8300	0.9009	0.2857	0.8604
G	0.0000	0.0400	0.0090	0.6190	0.1162
D	0.0000	0.0300	0.0180	0.0000	0.0232

The stages of this matrix are: 
1) Seedlings		S 
2) Juveniles		J
3) Vegetative		V
4) Reproductive individuals	G
5) Dormant plants	D
''',
	example='[S, J, V, G, D]'
	)

flow.input.pooled_matrix_file = TextFile

flow.task.RequestStageMatrices = InteractionPage(
	'http://biovel.googlecode.com/svn/tags/mpm-20131215/select_matrices.html',
	inputs = dict(
		title=String(description="Message displayed at top of page"),
		values=List[String](description="Values for which user will select input files"),
		field=String(description="Name of field in input port values"),
		multiple=String['true','false'](description="""true = select multiple input files per value
false = select a single input file per value"""),
		),
	outputs = dict(
		matrices=List[List[String]](description="""Contents of the files per value

Each element of the top-level list is related to each element of the input port values. For each value there is a list containing the contents of each file selected for a value. If the input port multiple is false, there will only be one string in each of these inner lists""")
		)
	)

"Select a stage matrix for each year" >> flow.task.RequestStageMatrices.input.title
"Year" >> flow.task.RequestStageMatrices.input.field
"false" >> flow.task.RequestStageMatrices.input.multiple
flow.input.years >> flow.task.RequestStageMatrices.input.values

flow.task.FlattenList = BeanshellCode(
'''flatten(inputs, outputs, depth) {
	for (i = inputs.iterator(); i.hasNext();) {
	    element = i.next();
		if (element instanceof Collection && depth > 0) {
			flatten(element, outputs, depth - 1);
		} else {
			outputs.add(element);
		}
	}
}

outputlist = new ArrayList();

flatten(inputlist, outputlist, 1);
''',
	inputs = dict(
		inputlist=List[List[String]]
		),
	outputs = dict(
		outputlist=List[String]
		)
	)

flow.task.RequestStageMatrices.output.matrices >> flow.task.FlattenList.input.inputlist

rserve = RServer()

import sys
sys.path.append('')
from util.r.file import ReadMatrixFromFile

flow.task.ReadStageMatrix = ReadMatrixFromFile(rserve)
# List[String] -> String = 1 level of iteration
flow.task.FlattenList.output.outputlist >> flow.task.ReadStageMatrix.input.matrix_file
flow.input.stages >> flow.task.ReadStageMatrix.input.xlabels
flow.input.stages >> flow.task.ReadStageMatrix.input.ylabels

flow.task.ReadPooledMatrix = ReadMatrixFromFile(rserve)
flow.input.pooled_matrix_file >> flow.task.ReadPooledMatrix.input.matrix_file
flow.input.stages >> flow.task.ReadPooledMatrix.input.xlabels
flow.input.stages >> flow.task.ReadPooledMatrix.input.ylabels

from util.r.format import ListR_to_RList

flow.task.CreateRListOfMatrices = ListR_to_RList(rserve)
flow.task.ReadStageMatrix.output.matrix >> flow.task.CreateRListOfMatrices.input.list_of_r_expressions


flow.task.AddNames = rserve.code('names(expr) <- labels', inputs=dict(labels=Vector[String]))
flow.task.CreateRListOfMatrices.output.r_list_of_expressions >> flow.task.AddNames.input.expr
flow.input.years >> flow.task.AddNames.input.labels

flow.task.CalculateYearEffect = NestedZapyFile('LTRE.py')
flow.task.AddNames.output.expr >> flow.task.CalculateYearEffect.input.matrices
flow.task.ReadPooledMatrix.output.matrix >> flow.task.CalculateYearEffect.input.pooled_matrix
'Years' >> flow.task.CalculateYearEffect.input.xlabel
flow.input.years >> flow.task.CalculateYearEffect.input.xticks
'Year Effect' >> flow.task.CalculateYearEffect.input.ylabel
'lightblue' >> flow.task.CalculateYearEffect.input.plot_colour
flow.task.CalculateYearEffect.extendUnusedInputs()

from util.r.format import PrettyPrint

flow.task.PrintAnalysis = PrettyPrint(rserve)
flow.task.CalculateYearEffect.output.LTRE_Analysis >> flow.task.PrintAnalysis.input.rexpr
flow.output.LTRE_Analysis = flow.task.PrintAnalysis.output.text

flow.task.PrintResults = PrettyPrint(rserve)
flow.task.CalculateYearEffect.output.LTRE_Results_RLn >> flow.task.PrintResults.input.rexpr
flow.output.LTRE_Results = flow.task.PrintResults.output.text

flow.output.LTRE_Graph = flow.task.CalculateYearEffect.output.graph


