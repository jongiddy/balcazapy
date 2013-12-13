# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title='Place Effect', author=u'Maria Paula Balcázar-Vargas, Jonathan Giddy and Gerard Oostermeijer')

flow.input.places = List[String](
	description="Site names",
	example="[Dwingeloo 1, Dwingeloo 2, Dwingeloo 3, Lochem, Terschelling]"
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
	'http://biovel.googlecode.com/svn/trunk/popmod/mpm/select_matrices.html',
	inputs = dict(
		title=String(description="Message displayed at top of page"),
		values=List[String](description="Values for which user will select input files"),
		field=String(description="Name of field in input port values"),
		multiple=String['true','false'](description="""true = select multiple input files per value
false = select a single input file per value"""),
		),
	outputs = dict(
		contents=List[List[String]](description="""Contents of the files per value

Each element of the top-level list is related to each element of the input port values. For each value there is a list containing the contents of each file selected for a value. If the input port multiple is false, there will only be one string in each of these inner lists""")
		)
	)

"Select multiple stage matrices from different years for each location" >> flow.task.RequestStageMatrices.input.title
"Location" >> flow.task.RequestStageMatrices.input.field
"true" >> flow.task.RequestStageMatrices.input.multiple
flow.input.places >> flow.task.RequestStageMatrices.input.values

rserve = RServer()

import sys
sys.path.append('')
from util.r.file import ReadMatrixFromFile

flow.task.ReadStageMatrix = ReadMatrixFromFile(rserve)
# List[List[String]] -> String = 2 levels of iteration
flow.task.RequestStageMatrices.output.contents >> flow.task.ReadStageMatrix.input.matrix_file
flow.input.stages >> flow.task.ReadStageMatrix.input.xlabels
flow.input.stages >> flow.task.ReadStageMatrix.input.ylabels

flow.task.ReadPooledMatrix = ReadMatrixFromFile(rserve)
flow.input.pooled_matrix_file >> flow.task.ReadPooledMatrix.input.matrix_file
flow.input.stages >> flow.task.ReadPooledMatrix.input.xlabels
flow.input.stages >> flow.task.ReadPooledMatrix.input.ylabels

from util.r.format import ListR_to_RList

flow.task.CreateListOfRMatrices = ListR_to_RList(rserve)
flow.task.ReadStageMatrix.output.matrix >> flow.task.CreateListOfRMatrices.input.list_of_r_expressions

flow.task.MeanMatrix = rserve.code('''
# mean(matrix) usually returns the mean of all values in the matrix
# mean(list of matrices) isn't present in base R, but the logical return value
# would be a list (or vector) of the mean of each matrix in the list.  However,
# package "popbio" overides mean for lists to return a matrix containing the
# mean of values at each coordinate in all the matrices.  To emphasise that we
# are calling this function, we call it with the function's full name, including
# type.
library(popbio)
mean_matrix <- mean.list(matrices)
''',
	inputs = dict(matrices = RExpression),
	outputs = dict(mean_matrix = RExpression)
	)

flow.task.CreateListOfRMatrices.output.r_list_of_expressions >> flow.task.MeanMatrix.input.matrices

flow.task.CreateRListOfMatrices = ListR_to_RList(rserve)
flow.task.MeanMatrix.output.mean_matrix >> flow.task.CreateRListOfMatrices.input.list_of_r_expressions


flow.task.AddNames = rserve.code('names(expr) <- labels', inputs=dict(labels=Vector[String]))
flow.task.CreateRListOfMatrices.output.r_list_of_expressions >> flow.task.AddNames.input.expr
flow.input.places >> flow.task.AddNames.input.labels

flow.task.CalculatePlaceEffect = NestedWorkflowFile('LTRE.py')
flow.task.AddNames.output.expr >> flow.task.CalculatePlaceEffect.input.matrices
flow.task.ReadPooledMatrix.output.matrix >> flow.task.CalculatePlaceEffect.input.pooled_matrix
'Places' >> flow.task.CalculatePlaceEffect.input.xlabel
flow.input.places >> flow.task.CalculatePlaceEffect.input.xticks
'Place Effect' >> flow.task.CalculatePlaceEffect.input.ylabel
'lightgreen' >> flow.task.CalculatePlaceEffect.input.plot_colour
flow.task.CalculatePlaceEffect.extendUnusedInputs()

from util.r.format import PrettyPrint

flow.task.PrintAnalysis = PrettyPrint(rserve)
flow.task.CalculatePlaceEffect.output.LTRE_Analysis >> flow.task.PrintAnalysis.input.rexpr
flow.output.LTRE_Analysis = flow.task.PrintAnalysis.output.text

flow.task.PrintResults = PrettyPrint(rserve)
flow.task.CalculatePlaceEffect.output.LTRE_Results_RLn >> flow.task.PrintResults.input.rexpr
flow.output.LTRE_Results = flow.task.PrintResults.output.text

flow.output.LTRE_Graph = flow.task.CalculatePlaceEffect.output.graph


