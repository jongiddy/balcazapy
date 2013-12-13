from balcaza.t2activity import *
from balcaza.t2types import *

def ReadMatrixFromFile(rserve):
	return rserve.file(
		'ReadMatrixFile.r',
		inputs = dict(
			matrix_file = TextFile,
			xlabels = Vector[String],
			ylabels = Vector[String]
		),
		outputs = dict(
			matrix = RExpression(description='An R matrix')
			)
		)

