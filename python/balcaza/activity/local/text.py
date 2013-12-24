from balcaza.t2types import *
from balcaza.t2activity import BeanshellCode

ByteArrayToString = BeanshellCode(
'''if ((bytes == void) || (bytes == null)) {
	throw new RuntimeException("The 'bytes' parameter must be specified");
}
if (encoding == void) {
	string = new String(bytes);
} else {
	string = new String(bytes, encoding);
}
''',
	inputs = dict(
		bytes = String,
		encoding = String
		),
	outputs = dict(
		string = String
		),
	defaultInput = 'bytes',
	name = 'ByteArrayToString'	
	)
