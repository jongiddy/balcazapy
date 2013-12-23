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

RequestStageMatrices = flow.task.RequestStageMatrices << InteractionPage(
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

RequestStageMatrices.input.title = "Select a stage matrix for each year"
RequestStageMatrices.input.field = "Year"
RequestStageMatrices.input.multiple = "false"
flow.input.years | RequestStageMatrices.input.values

FlattenList = flow.task.FlattenList << BeanshellCode(
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

RequestStageMatrices.output.matrices | FlattenList.input.inputlist

rserve = RServer()

import sys
sys.path.append('')
from util.r.file import ReadMatrixFromFile


ReadStageMatrix = flow.task.ReadStageMatrix << ReadMatrixFromFile(rserve)

# List[String] -> String = 1 level of iteration
FlattenList.output.outputlist | ReadStageMatrix.input.matrix_file
flow.input.stages | ReadStageMatrix.input.xlabels
flow.input.stages | ReadStageMatrix.input.ylabels


ReadPooledMatrix = flow.task.ReadPooledMatrix << ReadMatrixFromFile(rserve)

flow.input.pooled_matrix_file | ReadPooledMatrix.input.matrix_file
flow.input.stages | ReadPooledMatrix.input.xlabels
flow.input.stages | ReadPooledMatrix.input.ylabels


from util.r.format import ListR_to_RList
CreateRListOfMatrices = flow.task.CreateRListOfMatrices << ListR_to_RList(rserve)

ReadStageMatrix.output.matrix | CreateRListOfMatrices.input.list_of_r_expressions


AddNames = flow.task.AddNames << rserve.code(
	'names(expr) <- labels',
	inputs=dict(labels=Vector[String])
	)

CreateRListOfMatrices.output.r_list_of_expressions | AddNames.input.expr
flow.input.years | AddNames.input.labels


CalculateYearEffect = flow.task.CalculateYearEffect << NestedZapyFile('LTRE.py')

AddNames.output.expr | CalculateYearEffect.input.matrices
ReadPooledMatrix.output.matrix | CalculateYearEffect.input.pooled_matrix
'Years' | CalculateYearEffect.input.xlabel
flow.input.years | CalculateYearEffect.input.xticks
'Year Effect' | CalculateYearEffect.input.ylabel
'lightblue' | CalculateYearEffect.input.plot_colour
CalculateYearEffect.extendUnusedInputs()

from util.r.format import PrettyPrint

PrintAnalysis = flow.task.PrintAnalysis << PrettyPrint(rserve)
CalculateYearEffect.output.LTRE_Analysis | PrintAnalysis.input.rexpr
flow.output.LTRE_Analysis = PrintAnalysis.output.text

PrintResults = flow.task.PrintResults << PrettyPrint(rserve)
CalculateYearEffect.output.LTRE_Results_RLn | PrintResults.input.rexpr
flow.output.LTRE_Results = PrintResults.output.text

flow.output.LTRE_Graph = CalculateYearEffect.output.graph


