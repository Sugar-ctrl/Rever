class BaseAst:
    '''
    ast的基类
    '''
    pass


class GetAttr(BaseAst):
    r'''
    获取属性的ast节点
    正则：\.[a-zA-Z_][a-zA-Z0-9_]*
    '''

    def __init__(self, attrname: str):
        self.attrname: str = attrname


class GetAttrPtr(BaseAst):
    r'''
    获取属性指针的ast节点
    正则：\.&[a-zA-Z_][a-zA-Z0-9_]*
    '''

    def __init__(self, attrname: str):
        self.attrname: str = attrname


class GetVar(BaseAst):
    '''
    获取变量的ast节点
    正则：[a-zA-Z_][a-zA-Z0-9_]*
    '''

    def __init__(self, varname: str):
        self.varname: str = varname


class GetVarPtr(BaseAst):
    '''
    获取变量指针的ast节点
    正则：\&[a-zA-Z_][a-zA-Z0-9_]*
    '''

    def __init__(self, varname: str):
        self.varname: str = varname


class Literal(BaseAst):
    '''
    字面量的ast节点的基类
    '''
    pass


class KeywordOrOperator(BaseAst):
    '''
    关键字或运算符的ast节点
    '''

    def __init__(self, keyword: str):
        self.keyword: str = keyword


class IntLiteral(Literal):
    '''
    整数字面量的ast节点
    正则：[0-9]+ 或 0x[0-9a-fA-F]+ 或 0b[01]+
    '''

    def __init__(self, value: int):
        self.value: int = value


class StringLiteral(Literal):
    '''
    字符串字面量的ast节点
    正则：""
    '''

    def __init__(self, value: str):
        self.value: str = value


class BooleanLiteral(Literal):
    '''
    布尔字面量的ast节点
    正则：true|false
    '''

    def __init__(self, value: bool):
        self.value: bool = value


class NullLiteral(Literal):
    '''
    空字面量的ast节点
    正则：null
    '''


class FloatLiteral(Literal):
    '''
    浮点数字面量的ast节点
    正则：[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?
    '''

    def __init__(self, value: float):
        self.value: float = value


class CodeBlock(BaseAst):
    '''
    代码块的ast节点
    '''

    def __init__(self, blockindex: int):
        self.blockindex: int = blockindex
