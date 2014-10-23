# Copyright (C) 2013 Cardiff University
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

__all__ = ('Logical', 'Integer', 'Number', 'String', 'TextFile',
    'BinaryFile', 'PDF_File', 'PNG_Image', 'RExpression', 'List', 'Vector',
    'Optional')

import copy
from t2util import BeanshellEscapeString


class T2FlowType:

    def __init__(self, name, depth=0):
        assert isinstance(name, str), name
        self.name = name
        self.depth = depth
        self.dict = {}

    def __str__(self):
        return '%s%s' % (self.name, self.annotationsAsString())

    def hasAnnotation(self, name):
        return name in self.dict

    def getAnnotation(self, name):
        return self.dict[name]

    def annotationsAsString(self):
        if self.dict:
            annotations = ', '.join([('%s=%s' % (name, repr(value))) for name, value in self.dict.items()])
            return '(%s)' % annotations
        else:
            return ''

    def __call__(self, **kw):
        new = copy.copy(self)
        new.dict = kw
        return new

    def set(self, **kw):
        new = copy.copy(self)
        new.dict = self.dict.copy()
        new.dict.update(kw)
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
        script = "switch(s)\n{\n"
        for value in self.domain:
            script += 'case "%s":\n' % BeanshellEscapeString(value)
        script += """\tbreak;
default:
\tthrow RuntimeException("Invalid value");
}
"""
        from t2activity import BeanshellCode
        return BeanshellCode(script, inputs={'s': String},
            outputs={'s': String})

String = StringType('String')


class LogicalType(T2FlowType):

    domain = ('FALSE', 'TRUE')
    domainSet = frozenset(domain)

    def __init__(self, name):
        T2FlowType.__init__(self, name)

    def getAnnotation(self, name):
        value = T2FlowType.getAnnotation(self, name)
        if name == 'example' and (value not in self.domain):
            # Example can be set to any boolean (e.g. Python's True or False)
            # and will be mapped to the Taverna/R logical string value here
            value = self.domain[value]
            assert value in self.domain, value
        return value

    def getDomain(self):
        return self.domainSet

    def symanticType(self):
        return 'BOOL'

    def symanticVectorType(self):
        return 'BOOL_LIST'

    def validator(self, inputType):
        return StringType(self.name, self.domain).validator(inputType)

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
        return '%s%s%s' % (self.name, domain, self.annotationsAsString())

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
            script = "i=Integer.parseInt(s.trim());\n"
        elif isinstance(inputType, NumberType):
            script = "i=s.intValue();\n"
        else:
            raise RuntimeError('incompatible input to Integer')
        conditions = []
        if self.lower is not None:
            conditions.append("i<%d" % self.lower)
        if self.higher is not None:
            conditions.append("i>%d" % self.higher)
        condition = '||'.join(conditions)
        if condition:
            script += 'if(%s){throw new RuntimeException("integer out of bounds");}' % condition
        if script:
            from t2activity import BeanshellCode
            return BeanshellCode(script, inputs={'s': String}, outputs={'i': String})

    def integerValidator(self, inputType):
        conditions = []
        if self.lower is not None:
            if inputType.lower is None or inputType.lower < self.lower:
                conditions.append("i<%d" % self.lower)
        if self.higher is not None:
            if inputType.higher is None or inputType.higher > self.higher:
                conditions.append("i>%d" % self.higher)
        condition = '||'.join(conditions)
        if condition:
            script = 'if(%s){throw new RuntimeException("integer out of bounds");}' % condition
            from t2activity import BeanshellCode
            return BeanshellCode(script, inputs={'i': String}, outputs={'i': String})

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
            x = 'List[%s]%s' % (x, self.annotationsAsString())
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
