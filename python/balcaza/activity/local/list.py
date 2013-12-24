from balcaza.t2types import *
from balcaza.t2activity import BeanshellCode

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
		seperator = Option[String]
		),
	outputs = dict(
		concatenated = String
		),
	defaultInput = 'stringlist',
	name = 'MergeStringListToString'
)