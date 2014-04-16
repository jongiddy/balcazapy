# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(
    title='The Life Table Response Experiments year effect for multiple places workflow ',
    author=u'Maria Paula Balcázar-Vargas, Jonathan Giddy and Gerard Oostermeijer',
    description=u'''The Life Table Response Experiments year effect for multiple places workflow provides an environment to analyse two or more matrices (e.g., two or more matrices of different years of one place) of two or more different locations. The objective of this workflow is to determine the effects of the research years (2 or more) on lambda. This workflow performs a fixed LTRE, one way design (Caswell 2001).

LTRE is a retrospective analysis (Caswell 1989), beginning with data on the vital rates and on lambda under two or more sets of environmental conditions (in this case 2 or more years from different places) (Horvitz, Schemske and Caswell 1997). The goal of the analysis is to quantify the contribution of each of the vital rates to the variability in lambda. (Caswell 1989, 1996, 2001 in Horvitz, Schemske and Caswell 1997).

Fixed Treatments: Decomposing Years Treatment Effects

A fixed-effect analysis treats the matrices as representative of particular conditions, either experimental or natural (high vs. low nutrients in a one-way model, for example, or year and spatial location in a two-way model). The goal is to determine how much a treatment level (in this case year) on lambda is contributed by each of the vital rates. The analysis uses a linear approximation in which the sensitivities appear as slopes. The effect of a treatment on lambda depends on its effect on each matrix entry and on the sensitivity of lambda to that entry. (Horvitz, Schemske and Caswell 1997).

For more details of the analysis see: Retrospective Analyses: Fixed Treatments (page 262 in Horvitz, Schemske and Caswell 1997) and Chapter 10 Life Table Response Experiments (page 258 in Caswell 2001).

=============================================================================================

Literature

Caswell, H. 1989. The analysis of life table response experiments. I. Decomposition of treatment effects on population growth rate. Ecological Modelling 46: 221-237.

Caswell, H. 1996. Demography meets ecotoxicology: Untangling the population level effects of toxic substances. Pp. 255-292 in M. C. Newman and C. H. Jagoe, eds., Ecotoxicology: A Hierarchical Treatment. Lewis, Boca Raton, Fla.

Caswell, H. 2001. Matrix population models: Construction, analysis and interpretation, 2nd Edition. Sinauer Associates, Sunderland, Massachusetts.

Horvitz, C.C. and D.W. Schemske. 1995. Spatiotemporal Variation in Demographic Transitions of a Tropical Understory Herb: Projection Matrix Analysis. Ecological Monographs, 65:155-192

Horvitz, C., D.W. Schemske, and Hal Caswell. 1997. The relative "importance" of life-history stages to population growth: Prospective and retrospective analyses. In S. Tuljapurkar and H. Caswell. Structured population models in terrestrial and freshwater systems. Chapman and Hall, New York.

Oostermeijer J.G.B., M.L. Brugman, E.R. de Boer; H.C.M. Den Nijs. 1996. Temporal and Spatial Variation in the Demography of Gentiana pneumonanthe, a Rare Perennial Herb. The Journal of Ecology, Vol. 84(2): 153-166.

Stubben, C & B. Milligan. 2007. Estimating and Analysing Demographic Models Using the popbio Package in R. Journal of Statistical Software 22 (11): 1-23

Stubben, C., B. Milligan, P. Nantel. 2011. Package ‘popbio’. Construction and analysis of matrix population models. Version 2.3.1'''
    )

flow.input.places = List[String](
	description="Places: The list of places (two or more) where the research has being carried out.",
	example="[Dwingeloo 1, Dwingeloo 2, Dwingeloo 3, Lochem, Terschelling]"
	)

flow.input.years = List[Integer[1500,...,2100]](
	description="All years which start a period of transition. This should indicate two consecutive study periods",
	example="[1988, 1989]"
	)

flow.input.stages = List[String](
	description='''Stages: the names of the stages or categories of the input matrix.

In the following example, the matrix has 5 stages or categories:

The stages of this matrix are called:
1) Seedlings\t\t\tS
2) Juveniles\t\t\tJ
3) Vegetative\t\t\tV
4) Reproductive individuals\t\tG
5) Dormant plants\t\tD''',
	example='[S, J, V, G, D]'
	)

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

RequestStageMatrices.input.title = "For each location, select 2 or more stage matrices from consecutive years intervals."
RequestStageMatrices.input.field = "Location"
RequestStageMatrices.input.multiple = "true"
flow.input.places | RequestStageMatrices.input.values

rserve = RServer()

import sys
sys.path.append('')
from util.r.file import ReadMatrixFromFile

ReadStageMatrix = flow.task.ReadStageMatrix << ReadMatrixFromFile(rserve)

RequestStageMatrices.output.matrices |++ ReadStageMatrix.input.matrix_file
matrices_LLRn2 = ReadStageMatrix.output.matrix
flow.input.stages | ReadStageMatrix.input.xlabels
flow.input.stages | ReadStageMatrix.input.ylabels

flow.input.pooled_matrix_file = TextFile(
    description='''Weighted main Matrix in a .txt file format or what popbio (R package) calls pooled matrix (to see more details: Horvitz, Schemske and Caswell 1997; Horvitz, and Schemske 1995).

The pooled matrix is a better summary of the demography than a matrix of averages calculated over a number of matrices because of the way rarely observed transitions affect the values. If the averages are taken, transition events that happen to many individuals in one year and plot are given equal weighting to transition events that happen to few individuals in one year and plot ( Horvitz and Schemske 1995).
''',
    example='''0.0074\t0\t0\t7.9915\t0
0.1981\t0.0056\t0\t4.4289\t0
0.2467\t0.7087\t0.7015\t0.4220\t0.3380
0.0369\t0.0508\t0.1609\t0.4973\t0.1939
0\t0.0388\t0.0848\t0.0808\t0.4681'''
    )

ReadPooledMatrix = flow.task.ReadPooledMatrix << ReadMatrixFromFile(rserve)
flow.input.pooled_matrix_file | ReadPooledMatrix.input.matrix_file
flow.input.stages | ReadPooledMatrix.input.xlabels
flow.input.stages | ReadPooledMatrix.input.ylabels

Transpose = flow.task.Transpose << BeanshellFile(
	'transpose.bsh',
	inputs = dict(
		listDepth3 = List[List[List[Number]]]
		),
	outputs = dict(
		transposed = List[List[List[Number]]]
		)
	)

from balcaza.activity.rstats.list import ListRtoRList

MeanMatrix = flow.task.MeanMatrix << rserve.code('''
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
	outputs = dict(mean_matrix = RExpression),
	defaultInput = 'matrices',
	defaultOutput = 'mean_matrix'
	)

mean_matrices_LRn2 = matrices_LLRn2 |-- Transpose |+ ListRtoRList | MeanMatrix

AddNames = flow.task.AddNames << rserve.code(
	'names(expr) <- labels',
	inputs=dict(labels=Vector[String]),
	defaultInput='expr',
	defaultOutput='expr'
	)

flow.input.years | AddNames.input.labels

CalculatePlaceEffect = flow.task.CalculatePlaceEffect << NestedZapyFile('LTRE.py',
    inputs = dict(
        matrices = RExpression,
        pooled_matrix = RExpression,
        xticks = List[String],
        xlabel = String,
        plot_colour = String,
        plot_title = String(description='Plot title: Descriptive main title for labelling generated outputs (graphs).', example='LTRE, Gentiana pneumonanthe'),
        ylabel = String
        ),
    outputs = dict(
        LTRE_Analysis = RExpression(description='''LTRE_Analysis: Intermediary results showing the matrices calculated on the LTRE analysis per year. After this step the workflow sums up all the values per matrix giving us the final result: LTRE_ Results.''', example='''$`1988`
\tS\tJ\tV\tG\tD
S\t-0,00052453\t0\t0\t-0,103043507\t0
J\t-0,03495754\t-0,000665156\t0\t-0,152312111\t0
V\t-0,03814084\t-0,00607003\t-0,04351741\t-0,023654522\t-0,003417825
G\t-0,058844293\t0,002606578\t0,037617619\t0,129540602\t-0,00450503
D\t0\t-0,00236353\t-0,008211038\t-0,008574729\t0,005021163

$`1989`
\tS\tJ\tV\tG\tD
S\t-0,000495382\t0\t0\t-0,112706023\t0
J\t-0,02925375\t-0,000790648\t0\t-0,111478812\t0
V\t-0,019606058\t0,036731763\t-0,025998876\t0,009560876\t0,005126723
G\t-0,027846831\t-0,033431783\t-0,10417847\t-0,066688407\t-0,014491732
D\t0\t-0,008364033\t0,001389627\t0,000672706\t-0,002462745
'''),
        graph = PNG_Image(description='''LTRE_Graph: Creates a histogram to display the LTRE_Results (Fig 12 in the documentation). The year effect is shown in the Figure. In this example: The year 1989 had the largest negative effect on lambda, and no year had a positive effect.'''),
        LTRE_Results = List[Number],
        LTRE_Results_RLn = RExpression
        )
)

mean_matrices_LRn2 |- ListRtoRList | AddNames | CalculatePlaceEffect.input.matrices

ReadPooledMatrix.output.matrix | CalculatePlaceEffect.input.pooled_matrix
CalculatePlaceEffect.input.xlabel = 'Year'
flow.input.years | CalculatePlaceEffect.input.xticks
CalculatePlaceEffect.input.ylabel = 'Year Effect'
CalculatePlaceEffect.input.plot_colour = 'lightblue'
CalculatePlaceEffect.extendUnusedInputs()

from balcaza.activity.rstats.format import RExpressionToString

PrintAnalysis = flow.task.PrintAnalysis << RExpressionToString(rserve)
flow.output.LTRE_Analysis = String(description='''LTRE_Analysis: Intermediary results showing the matrices calculated on the LTRE analysis per year. After this step the workflow sums up all the values per matrix giving us the final result: LTRE_ Results.''', example='''$`1988`
\tS\tJ\tV\tG\tD
S\t-0,00052453\t0\t0\t-0,103043507\t0
J\t-0,03495754\t-0,000665156\t0\t-0,152312111\t0
V\t-0,03814084\t-0,00607003\t-0,04351741\t-0,023654522\t-0,003417825
G\t-0,058844293\t0,002606578\t0,037617619\t0,129540602\t-0,00450503
D\t0\t-0,00236353\t-0,008211038\t-0,008574729\t0,005021163

$`1989`
\tS\tJ\tV\tG\tD
S\t-0,000495382\t0\t0\t-0,112706023\t0
J\t-0,02925375\t-0,000790648\t0\t-0,111478812\t0
V\t-0,019606058\t0,036731763\t-0,025998876\t0,009560876\t0,005126723
G\t-0,027846831\t-0,033431783\t-0,10417847\t-0,066688407\t-0,014491732
D\t0\t-0,008364033\t0,001389627\t0,000672706\t-0,002462745
''')
CalculatePlaceEffect.output.LTRE_Analysis | PrintAnalysis | flow.output.LTRE_Analysis

PrintResults = flow.task.PrintResults << RExpressionToString(rserve)
flow.output.LTRE_Results = String(
    description='LTRE_ Results: The results of the LTRE per year. These are the generated values of the plotted LTRE graph.',
    example='''1988\t1989
-0.3140161\t-0.5043119''')
CalculatePlaceEffect.output.LTRE_Results_RLn | PrintResults | flow.output.LTRE_Results

CalculatePlaceEffect.output.graph | flow.output.LTRE_Graph

