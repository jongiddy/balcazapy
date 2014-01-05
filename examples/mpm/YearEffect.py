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

from balcaza.activity.local.list import FlattenList

rserve = RServer()

import sys
sys.path.append('')
from util.r.file import ReadMatrixFromFile

ReadStageMatrix = flow.task.ReadStageMatrix << ReadMatrixFromFile(rserve)

RequestStageMatrices.output.matrices | FlattenList |+ ReadStageMatrix.input.matrix_file
flow.input.stages | ReadStageMatrix.input.xlabels
flow.input.stages | ReadStageMatrix.input.ylabels


ReadPooledMatrix = flow.task.ReadPooledMatrix << ReadMatrixFromFile(rserve)

flow.input.pooled_matrix_file | ReadPooledMatrix.input.matrix_file
flow.input.stages | ReadPooledMatrix.input.xlabels
flow.input.stages | ReadPooledMatrix.input.ylabels


from balcaza.activity.rstats.list import ListRtoRList

AddNames = flow.task.AddNames << rserve.code(
	'names(expr) <- labels',
	inputs=dict(labels=Vector[String]),
	defaultInput='expr',
	defaultOutput='expr'
	)

flow.input.years | AddNames.input.labels

CalculateYearEffect = flow.task.CalculateYearEffect << NestedZapyFile('LTRE.py',
    inputs = dict(
        matrices = RExpression,
        pooled_matrix = RExpression,
        xticks = List[String],
        xlabel = String,
        plot_colour = String,
        plot_title = String,
        ylabel = String
        ),
    outputs = dict(
        LTRE_Analysis = RExpression,
        graph = PNG_Image,
        LTRE_Results = List[Number],
        LTRE_Results_RLn = RExpression
        )
)

ReadStageMatrix.output.matrix |- ListRtoRList | AddNames | CalculateYearEffect.input.matrices
ReadPooledMatrix.output.matrix | CalculateYearEffect.input.pooled_matrix
CalculateYearEffect.input.xlabel = 'Years'
flow.input.years | CalculateYearEffect.input.xticks
CalculateYearEffect.input.ylabel = 'Year Effect'
CalculateYearEffect.input.plot_colour = 'lightblue'
CalculateYearEffect.extendUnusedInputs()

from balcaza.activity.rstats.format import RExpressionToString

PrintAnalysis = flow.task.PrintAnalysis << RExpressionToString(rserve)
CalculateYearEffect.output.LTRE_Analysis | PrintAnalysis | flow.output.LTRE_Analysis

PrintResults = flow.task.PrintResults << RExpressionToString(rserve)
CalculateYearEffect.output.LTRE_Results_RLn | PrintResults | flow.output.LTRE_Results

CalculateYearEffect.output.graph | flow.output.LTRE_Graph
