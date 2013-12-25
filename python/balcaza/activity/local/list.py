from balcaza.t2types import *
from balcaza.t2activity import BeanshellCode

FlattenList = BeanshellCode(
'''flatten(inputs, outputs, depth) {
	for (i = inputs.iterator(); i.hasNext();) {
	    element = i.next();
		if (element instanceof Collection && depth > 0) {
			flatten(element, outputs, depth - 1);
		} else {
			outputs.add(element);
		}
	}
}

outputlist = new ArrayList();

flatten(inputlist, outputlist, 1);
''',
	inputs = dict(
		inputlist = List[List[String]]
		),
	outputs = dict(
		outputlist = List[String]
		),
	name = 'FlattenList'	
	)

MergeStringListToString = BeanshellCode(
'''String seperatorString = "\\n";
if (seperator != void) {
	seperatorString = seperator;
}
StringBuffer sb = new StringBuffer();
for (Iterator i = stringlist.iterator(); i.hasNext();) {
	String item = (String) i.next();
	sb.append(item);
	if (i.hasNext()) {
		sb.append(seperatorString);
	}
}
concatenated = sb.toString();
''',
	inputs = dict(
		stringlist = List[String],
		seperator = Optional[String]
		),
	outputs = dict(
		concatenated = String
		),
	defaultInput = 'stringlist',
	name = 'MergeStringListToString'
)

RemoveStringDuplicates = BeanshellCode(
'''List strippedlist = new ArrayList();
for (Iterator i = stringlist.iterator(); i.hasNext();) {
	String item = (String) i.next();
	if (strippedlist.contains(item) == false) {
		strippedlist.add(item);
	}
}
''',
	inputs = dict(
		stringlist = List[String]
		),
	outputs = dict(
		strippedlist = List[String]
		),
	name = 'RemoveStringDuplicates'	
	)
