from balcaza.t2types import RExpression, TextFile

def RExpressionToString(rserve):
	return rserve.code(
		'''sink(text)
print(rexpr)
sink()
''',
		inputs = dict(
			rexpr = RExpression
			),
		defaultInput = 'rexpr',
		outputs = dict(
			text = TextFile
			),
		defaultOutput = 'text'
		)
