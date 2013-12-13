# -*- coding: utf-8 -*-
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title='Life Table Response Experiment')

rserve = RServer()

flow.task.LTRE = rserve.code('''
library(popbio)
LTRE_Analysis <- LTRE(matrices, pooled_matrix)
''',
	inputs = dict(
		matrices=RExpression,
		pooled_matrix=RExpression
		),
	outputs = dict(
		LTRE_Analysis=RExpression
		)
	)

flow.task.LTRE.extendUnusedInputs()
flow.output.LTRE_Analysis = flow.task.LTRE.output.LTRE_Analysis

flow.task.PlotLTRE = rserve.file(
	'PlotLTRE.r',
	inputs = dict(
		LTRE_Analysis=RExpression,
		xticks=Vector[String],
		plot_title=String,
		xlabel=String,
		ylabel=String,
		plot_colour=String
		),
	outputs = dict(
		LTRE_Results_RLn=RExpression,
		LTRE_Results=Vector[Number],
		graph=PNG_Image
		)
	)

flow.task.LTRE.output.LTRE_Analysis >> flow.task.PlotLTRE.input.LTRE_Analysis
flow.task.PlotLTRE.extendUnusedPorts()
