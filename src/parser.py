from enum import Enum, auto

class UnitType(Enum):
    """
    单位类型
    """
    GET_ATTR = auto()
    GET_ATTR_PTR = auto()
    VAR = auto()
    VAR_PTR = auto()
    KEYWORD = auto()
    LITERAL = auto()
    CODE_BLOCK = auto()

def parse(tokens: list[str]):
    """
    解析tokens列表
    """