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

flow = Workflow(title = 'DoubleTheSum')

rserve = RServer()

# Using inputMap and outputMap in Rserve scripts has two uses:
# 1. it can map from R names containing dots to Taverna names with no dots
# 2. it can output variables in multiple formats (e.g. RExpression and Vector
flow.task.sum << rserve.code('total <- sum(my.vals)',
	inputs = dict(vals = Vector[Integer[0,...,100]]),
	inputMap = dict(vals = 'my.vals'), # Input "vals" maps to R variable "my.vals"
	outputs = dict(sum = Integer, total = RExpression),
	outputMap = dict(sum = 'total') # Output "sum" maps to R variable "total"
	)

flow.task.double << rserve.code('out1 <- 2 * in1', outputs = dict(out1 = Integer))

# We can use R variable names directly, even if they are not mentioned in the
# inputs and outputs, and they will be transferred as RExpressions
flow.task.sum.output.total | flow.task.double.input.in1

flow.task.sum.extendUnusedPorts()
flow.task.double.extendUnusedOutputs()
