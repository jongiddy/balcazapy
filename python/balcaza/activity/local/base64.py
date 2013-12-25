from balcaza.t2types import *
from balcaza.t2activity import BeanshellCode

DecodeBase64toBytes = BeanshellCode(
'''import org.apache.commons.codec.binary.Base64;
bytes = Base64.decodeBase64(base64.getBytes());''',
	inputs = dict(
		base64 = String
		),
	outputs = dict(
		bytes = String
		),
	name = 'DecodeBase64toBytes'	
	)

EncodeBytesToBase64 = BeanshellCode(
'''import org.apache.commons.codec.binary.Base64;
base64 = new String(Base64.encodeBase64(bytes));''',
	inputs = dict(
		bytes = String
		),
	outputs = dict(
		base64 = String
		),
	name = 'EncodeBytesToBase64'	
	)