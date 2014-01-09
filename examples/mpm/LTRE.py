# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Cardiff University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title='Life Table Response Experiment')

rserve = RServer()

LTRE = flow.task.LTRE << rserve.code('''
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

LTRE.extendUnusedPorts()

PlotLTRE = flow.task.PlotLTRE << rserve.file(
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

LTRE.output.LTRE_Analysis | PlotLTRE.input.LTRE_Analysis
PlotLTRE.extendUnusedPorts()
