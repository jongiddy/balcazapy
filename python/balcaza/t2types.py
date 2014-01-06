__all__ = ('Logical', 'Integer', 'Number', 'String', 'TextFile',
    'BinaryFile', 'PDF_File', 'PNG_Image', 'RExpression', 'List', 'Vector', 
    'Optional')

import copy
from t2util import BeanshellEscapeString

class T2FlowType:

    def __init__(self, name, depth=0):
        self.name = name
        self.depth = depth
        self.dict = {}

    def __str__(self):
        return self.name

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

class OptionalMarker:

    def __getitem__(self, type):
        return type

# currently Optional[type] is a null operation, just for documentation
# However, we could use it to ensure no non-optional inputs are unconnected
Optional = OptionalMarker()

class StringType(T2FlowType):

    def __init__(self, name, domain=None):
        T2FlowType.__init__(self, name)
        self.domain = domain

    def __getitem__(self, domain):
        if isinstance(domain, tuple):
            return StringType(self.name, domain)
        else:
            return StringType(self.name, (domain,))

    def symanticType(self):
        return 'STRING'

    def symanticVectorType(self):
        return 'STRING_LIST'

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
        from t2activity import BeanshellCode
        return BeanshellCode(script, inputs={'input': String}, 
            outputs={'output': String})

String = StringType('String')

class LogicalType(T2FlowType):

    domain = ('FALSE', 'TRUE')
    domainSet = frozenset(domain)

    def __init__(self, name):
        T2FlowType.__init__(self, name)

    def getDomain(self):
        return self.domainSet

    def symanticType(self):
        return 'BOOL'

    def symanticVectorType(self):
        return 'BOOL_LIST'

    def validator(self, inputType):
        return StringType(self.domain).validator(inputType)

Logical = LogicalType('Logical')

class IntegerType(T2FlowType):

    def __init__(self, name, lower=None, higher=None):
        T2FlowType.__init__(self, name)
        if lower is not None and higher is not None and lower > higher:
            raise RuntimeError('lower bound greater than upper bound')
        self.lower = lower
        self.higher = higher

    def __str__(self):
        if self.lower is None:
            if self.higher is None:
                domain = ''
            else:
                domain = '[...,%d]' % self.higher
        else:
            if self.higher is None:
                domain = '[%d,...]' % self.lower
            else:
                domain = '[%d,...,%d]' % (self.lower, self.higher)
        return '%s%s' % (self.name, domain)

    def symanticType(self):
        return 'INTEGER'

    def symanticVectorType(self):
        return 'INTEGER_LIST'

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
        return IntegerType(self.name, lower, higher)

    def validator(self, inputType):
        if isinstance(inputType, ListType):
            inputType = inputType.baseType
        if isinstance(inputType, IntegerType):
            return self.integerValidator(inputType)
        if isinstance(inputType, StringType):
            script = "output = Integer.parseInt(input.trim());\n"
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
            from t2activity import BeanshellCode
            return BeanshellCode(script, inputs={'input': String}, outputs={'output': String})

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
            from t2activity import BeanshellCode
            return BeanshellCode(script, inputs={'input': T2FlowType()}, outputs={'output': T2FlowType()})

Integer = IntegerType('Integer')

class NumberType(T2FlowType):

    def symanticType(self):
        return 'DOUBLE'

    def symanticVectorType(self):
        return 'DOUBLE_LIST'

Number = NumberType('Number')

class BinaryFileType(T2FlowType):

    def symanticType(self):
        return 'PNG_FILE'

BinaryFile = BinaryFileType('BinaryFile')

PDF_File = BinaryFileType('PDF_File')

PNG_Image = BinaryFileType('PNG_Image')

class TextFileType(T2FlowType):

    def symanticType(self):
        return 'TEXT_FILE'

TextFile = TextFileType('TextFile')

class ListType(T2FlowType):

    def __init__(self, name, elementType, depth=None):
        if depth is not None:
            # this option allows the creation of a list of strings of the same
            # depth as another list type, to represent the unchecked input ports 
            self.baseType = elementType
            depth = depth
        elif isinstance(elementType, ListType):
            self.baseType = elementType.baseType
            depth = elementType.depth + 1
        else:
            self.baseType = elementType
            depth = elementType.depth + 1
        T2FlowType.__init__(self, name, depth)

    def __str__(self):
        x = str(self.baseType)
        for i in range(self.depth):
            x = 'List[%s]' % x
        return x

    def validator(self, inputType):
        return self.baseType.validator(inputType)

class SeqFactory:

    def __init__(self, name, seqType):
        self.name = name
        self.seqType = seqType

    def __getitem__(self, elementType):
        return self.seqType(self.name, elementType)

List = SeqFactory('List', ListType)

class VectorType(ListType):

    def __init__(self, name, elementType):
        if not hasattr(elementType, 'symanticVectorType'):
            raise RuntimeError('Invalid Vector type')
        ListType.__init__(self, name, elementType)

    def symanticType(self):
        return self.baseType.symanticVectorType()

Vector = SeqFactory('Vector', VectorType)

class RExpressionType(T2FlowType):

    def __init__(self, name):
        T2FlowType.__init__(self, name, 1)

    def symanticType(self):
        return 'R_EXP'

RExpression = RExpressionType('RExpression')
