
from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

def PrettyPrint(rserve):
	return rserve.code('''
sink(text)
print(rexpr)
sink()
''',
		inputs = dict(
			rexpr = RExpression
		),
		outputs = dict(
			text = TextFile
			)
		)


def ListR_to_RList(rserve):
	flow = Workflow(
	    title='Convert a Taverna list of RExpressions to an R list',
	    author='Jonathan Giddy',
	    description="""This workflow accepts a Taverna list of arbitrary R expressions and returns a single R expression representing an R list containing the original expressions.

	This workflow relies on the current Taverna behaviour of an R expression being represented by a list of strings containing the deparsed expression. If this changes, this workflow will likely break.

	The first BeanShell converts each R expression (actually a list of strings) to a single string. This uses implicit iteration to do this for each R expression, so input port depth is 2 but the BeanShell input depth is 1. 

	The second Beanshell creates a comma-separated list of the deparsed R expressions and wraps the string with the R list() function. So now we have a single string s that can be turned into an R list using eval(parse(text=s)).

	But RShell already does that parsing for us, so we just need to ensure the string looks like an R expression by turning it into a list of strings. So we actually output a 1-element list containing the string.

	Version 1: initial implementation
	Version 2: reduce number of BeanShells
	""")

	Flatten = flow.task.FlattenListOfStringsToString << BeanshellFile(
	    "FlattenList.bsh",
	    inputs = dict(stringlist=RExpression),
	    outputs = dict(concatenated=String)
	    )

	flow.input.list_of_r_expressions = List[RExpression]
	flow.input.list_of_r_expressions >> Flatten.input.stringlist

	Combine = flow.task.CombineListOfStringsIntoRList << BeanshellFile(
	    "StringsToRList.bsh",
	    inputs = dict(stringlist=List[String]),
	    outputs = dict(output=List[String])
	    )

	Flatten.output.concatenated >> Combine.input.stringlist

	flow.output.r_list_of_expressions = Combine.output.output

	return NestedWorkflow(flow)
