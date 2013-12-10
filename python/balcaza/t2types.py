__all__ = ('Logical', 'Integer', 'Number', 'String', 'TextFile', 'PDF_File', 
    'PNG_Image', 'RExpression', 'List', 'Vector')

import copy
from t2util import BeanshellEscapeString
from t2activity import BeanshellActivity

class T2FlowType:

    def __init__(self, depth=0):
        self.depth = depth
        self.dict = {}

    def __call__(self, **kw):
        new = copy.copy(self)
        new.dict = kw
        return new

    def getDomain(self):
        # return all possible values of this type as a (frozen) set of strings. 
        # Return None if domain is too large or not possible to represent.
        return None

    def getDepth(self):
        return self.depth

    def validator(self, inputType):
        return None

class StringType(T2FlowType):

    def __init__(self, domain=None):
        T2FlowType.__init__(self)
        self.domain = domain

    def __getitem__(self, domain):
        if isinstance(domain, tuple):
            return StringType(domain)
        else:
            return StringType((domain,))

    def symanticType(self):
        return 'STRING'

    def getDomain(self):
        if self.domain is not None:
            return frozenset(self.domain)
        else:
            return None

    def validator(self, inputType):
        if isinstance(inputType, ListType):
            inputType = inputType.baseType
        if self.domain is None:
            # this string doesn't care what value it has, so do not validate
            return None
        inputDomain = inputType.getDomain()
        if inputDomain is not None and inputDomain <= self.getDomain():
            # the input string must be one of our valid strings, so do not validate
            return None
        script = "switch(input)\n{\n"
        for value in self.domain:
            script += 'case "%s":\n' % BeanshellEscapeString(value)
        script += """\toutput = input;
\tbreak;
default:
\tthrow RuntimeException("Invalid value");
}
"""
        return BeanshellActivity(script, inputs={'input': T2FlowType()}, 
            outputs={'output': T2FlowType()})

String = StringType()

class LogicalType(T2FlowType):

    domain = ('FALSE', 'TRUE')
    domainSet = frozenset(domain)

    def __init__(self):
        T2FlowType.__init__(self)

    def getDomain(self):
        return self.domainSet

    def symanticType(self):
        return 'BOOL'

    def validator(self, inputType):
        return StringType(self.domain).validator(inputType)

Logical = LogicalType()

class IntegerType(T2FlowType):

    def __init__(self, lower=None, higher=None):
        T2FlowType.__init__(self)
        if lower is not None and higher is not None and lower > higher:
            raise RuntimeError('lower bound greater than upper bound')
        self.lower = lower
        self.higher = higher

    def symanticType(self):
        return 'INTEGER'

    def __getitem__(self, domain):
        if not isinstance(domain, tuple):
            raise RuntimeError('unrecognised Integer range')
        if len(domain) == 2:
            if domain[0] == Ellipsis:
                lower = None
                higher = domain[1]
            elif domain[1] == Ellipsis:
                lower = domain[0]
                higher = None
            else:
                raise RuntimeError('unrecognised Integer range')
        elif len(domain) == 3 and domain[1] == Ellipsis:
            lower = domain[0]
            higher = domain[2]
        else:
            raise RuntimeError('unrecognised Integer range')
        return IntegerType(lower, higher)

    def validator(self, inputType):
        if isinstance(inputType, ListType):
            inputType = inputType.baseType
        if isinstance(inputType, IntegerType):
            return self.integerValidator(inputType)
        if isinstance(inputType, StringType):
            script = "output = Integer.parseInt(String.trim(input));\n"
        elif isinstance(inputType, NumberType):
            script = "output = input.intValue();\n"
        else:
            raise RuntimeError('incompatible input to Integer')
        conditions = []
        if self.lower is not None:
            conditions.append("output < %d" % self.lower)
        if self.higher is not None:
            conditions.append("output > %d" % self.higher)
        condition = ' || '.join(conditions)
        if condition:
            script += 'if (%s) {\n  throw new RuntimeException("integer out of bounds");\n}\n' % condition
        if script:
            return BeanshellActivity(script, inputs={'input': T2FlowType()}, outputs={'output': T2FlowType()})

    def integerValidator(self, inputType):
        conditions = []
        if self.lower is not None:
            if inputType.lower is None or inputType.lower < self.lower:
                conditions.append("output < %d" % self.lower)
        if self.higher is not None:
            if inputType.higher is None or inputType.higher > self.higher:
                conditions.append("output > %d" % self.higher)
        condition = ' || '.join(conditions)
        if condition:
            script = '''output = input;\nif (%s) {\n  throw new RuntimeException("integer out of bounds");\n}\n''' % condition
            return BeanshellActivity(script, inputs={'input': T2FlowType()}, outputs={'output': T2FlowType()})

Integer = IntegerType()

class NumberType(T2FlowType):

    def symanticType(self):
        return 'DOUBLE'

Number = NumberType()
class PNG_ImageType(T2FlowType):
    
    def symanticType(self):
        return 'PNG_FILE'

PNG_Image = PNG_ImageType()

PDF_File = PNG_Image

class TextFileType(T2FlowType):

    def symanticType(self):
        return 'TEXT_FILE'

TextFile = TextFileType()

VectorBaseType = {
    Logical: 'BOOL_LIST',
    Integer: 'INTEGER_LIST',
    Number: 'DOUBLE_LIST',
    String: 'STRING_LIST'
}

class ListType(T2FlowType):

    def __init__(self, elementType, depth=None):
        if depth is not None:
            self.baseType = elementType
            depth = depth
        elif isinstance(elementType, ListType):
            self.baseType = elementType.baseType
            depth = elementType.depth + 1
        else:
            self.baseType = elementType
            depth = elementType.depth + 1
        T2FlowType.__init__(self, depth)

    def validator(self, inputType):
        return self.baseType.validator(inputType)

    def symanticType(self):
        return VectorBaseType[self.baseType]

class ListFactory:

    def __getitem__(self, elementType):
        return ListType(elementType)

List = ListFactory()

class VectorFactory:

    def __getitem__(self, elementType):
        if isinstance(elementType, ListType):
            raise RuntimeError('Vector can not have depth > 1')
        if not VectorBaseType.has_key(elementType):
            raise RuntimeError('Invalid Vector type')
        return ListType(elementType)

Vector = VectorFactory()

class RExpressionType(T2FlowType):

    def __init__(self):
        T2FlowType.__init__(self, 1)

    def symanticType(self):
        return 'R_EXP'

RExpression = RExpressionType()
