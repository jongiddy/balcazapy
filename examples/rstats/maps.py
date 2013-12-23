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
