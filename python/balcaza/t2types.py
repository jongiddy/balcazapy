__all__ = ('Boolean', 'Integer', 'Number', 'String', 'TextFile', 'PNGImage',
    'RExpression', 'List', 'Vector')

import copy

class T2FlowType:

    def __init__(self, depth=0):
        self.depth = depth
        self.dict = {}

    def __call__(self, **kw):
        new = copy.copy(self)
        new.dict = kw
        return new

    def getDepth(self):
        return self.depth

    def validator():
        return None

class StringType(T2FlowType):

    def symanticType(self):
        return 'STRING'

String = StringType()

class BooleanType(T2FlowType):

    def symanticType(self):
        return 'BOOL'

Boolean = BooleanType()

integerValidatorScript = '''Integer.parseInt(input);
'''

class IntegerType(T2FlowType):

    def symanticType(self):
        return 'INTEGER'

    def validator():
        import t2activity
        t2activity.BeanshellTask(integerValidatorScript, {'input': T2FlowType},
            {'output': T2FlowType})

Integer = IntegerType()

class NumberType(T2FlowType):

    def symanticType(self):
        return 'DOUBLE'

Number = NumberType()
class PNGImageType(T2FlowType):
    
    def symanticType(self):
        return 'PNG_FILE'

PNGImage = PNGImageType()

class TextFileType(T2FlowType):

    def symanticType(self):
        return 'TEXT_FILE'

TextFile = TextFileType()

VectorBaseType = {
    Boolean: 'BOOL_LIST',
    Integer: 'INTEGER_LIST',
    Number: 'DOUBLE_LIST',
    String: 'STRING_LIST'
}

class ListType(T2FlowType):

    def __init__(self, elementType):
        if isinstance(elementType, ListType):
            self.baseType = elementType.baseType
            depth = elementType.depth + 1
        else:
            self.baseType = elementType
            depth = 1
        T2FlowType.__init__(self, depth)

    def validator(self):
        return self.baseType.validator()

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
