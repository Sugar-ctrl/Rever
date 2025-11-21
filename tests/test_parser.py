import pytest
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lexer import tokenize
from src.parser import parse
import src.ast_types as ast


# 创建一个mock的ReverObject类
class MockReverObject:
    def __init__(self, value=None):
        self.value = value
        self.attrs = {}
        self.ptr = None

@pytest.fixture(autouse=True)
def mock_rever_object(monkeypatch):
    """自动应用于所有测试的fixture，用于mock ReverObject"""
    monkeypatch.setattr('src.runtime.objects.ReverObject', MockReverObject)


def test_basic_tokens():
    """测试基本 token 解析"""
    code = '42 &x = "hello" true false null'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 7
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 42        # type: ignore
    assert isinstance(asts[1], ast.GetVarPtr)
    assert asts[1].varname == 'x'
    assert isinstance(asts[2], ast.KeywordOrOperator)
    assert asts[2].keyword == '='
    assert isinstance(asts[3], ast.StringLiteral)
    assert asts[3].value.value == 'hello'        # type: ignore
    assert isinstance(asts[4], ast.BooleanLiteral)
    assert asts[4].value.value == True        # type: ignore
    assert isinstance(asts[5], ast.BooleanLiteral)
    assert asts[5].value.value == False        # type: ignore
    assert isinstance(asts[6], ast.NullLiteral)

def test_member_access():
    """测试成员访问"""
    code = 'obj .attr ptr @ .method'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 5
    assert isinstance(asts[0], ast.GetVar)
    assert asts[0].varname == 'obj'
    assert isinstance(asts[1], ast.GetAttr)
    assert asts[1].attrname == 'attr'
    assert isinstance(asts[2], ast.GetVar)
    assert asts[2].varname == 'ptr'
    assert isinstance(asts[3], ast.KeywordOrOperator)
    assert asts[3].keyword == '@'
    assert isinstance(asts[4], ast.GetAttr)
    assert asts[4].attrname == 'method'

def test_simple_block():
    """测试简单代码块"""
    code = '{ 42 &x = }'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 1
    assert isinstance(asts[0], ast.CodeBlock)
    assert asts[0].blockindex == 0
    
    assert len(blocks) == 1
    block_content = blocks[0]
    assert len(block_content) == 3
    assert isinstance(block_content[0], ast.IntLiteral)
    assert isinstance(block_content[1], ast.GetVarPtr)
    assert isinstance(block_content[2], ast.KeywordOrOperator)

def test_nested_blocks():
    """测试嵌套代码块"""
    code = '{ { 1 } { 2 } }'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 1
    assert isinstance(asts[0], ast.CodeBlock)
    assert len(blocks) == 3
    outer_block = blocks[asts[0].blockindex]
    assert len(outer_block) == 2
    assert isinstance(outer_block[0], ast.CodeBlock)
    assert isinstance(outer_block[1], ast.CodeBlock)
    inner_block_1 = blocks[outer_block[0].blockindex]
    assert len(inner_block_1) == 1
    assert isinstance(inner_block_1[0], ast.IntLiteral)
    assert inner_block_1[0].value.value == 1        # type: ignore
    inner_block_2 = blocks[outer_block[1].blockindex]
    assert len(inner_block_2) == 1
    assert isinstance(inner_block_2[0], ast.IntLiteral)
    assert inner_block_2[0].value.value == 2        # type: ignore


def test_complex_expression():
    """测试复杂表达式"""
    code = '3 4 + &result = result @ 2 *'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    expected_types = [
        ast.IntLiteral,      # 3
        ast.IntLiteral,      # 4  
        ast.KeywordOrOperator, # +
        ast.GetVarPtr,       # &result
        ast.KeywordOrOperator, # =
        ast.GetVar,          # result
        ast.KeywordOrOperator, # @
        ast.IntLiteral,      # 2
        ast.KeywordOrOperator  # *
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert isinstance(asts[i], expected_type)

def test_error_unmatched_brace():
    """测试不匹配的大括号"""
    with pytest.raises(SyntaxError, match="Unmatched"):
        code = '{ 42'
        tokens = tokenize(code)
        parse(tokens)
    
    with pytest.raises(SyntaxError, match="Unmatched"):
        code = '42 }'
        tokens = tokenize(code)
        parse(tokens)

def test_empty_block():
    """测试空代码块"""
    code = '{}'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 1
    assert isinstance(asts[0], ast.CodeBlock)
    assert len(blocks[0]) == 0

# test_parser.py (补充部分)

def test_attr_ptr_access():
    """测试属性指针访问"""
    code = 'obj .&attr ptr @ .&method'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 5
    assert isinstance(asts[0], ast.GetVar)
    assert asts[0].varname == 'obj'
    assert isinstance(asts[1], ast.GetAttrPtr)
    assert asts[1].attrname == 'attr'
    assert isinstance(asts[2], ast.GetVar)
    assert asts[2].varname == 'ptr'
    assert isinstance(asts[3], ast.KeywordOrOperator)
    assert asts[3].keyword == '@'
    assert isinstance(asts[4], ast.GetAttrPtr)
    assert asts[4].attrname == 'method'

def test_hex_integer():
    """测试十六进制整数"""
    code = '0x1A 0xFF 0xabc'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 3
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 0x1A        # type: ignore
    assert isinstance(asts[1], ast.IntLiteral)
    assert asts[1].value.value == 0xFF        # type: ignore
    assert isinstance(asts[2], ast.IntLiteral)
    assert asts[2].value.value == 0xABC        # type: ignore

def test_binary_integer():
    """测试二进制整数"""
    code = '0b1010 0b1111 0b1'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 3
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 0b1010  # 10        # type: ignore
    assert isinstance(asts[1], ast.IntLiteral)
    assert asts[1].value.value == 0b1111  # 15        # type: ignore
    assert isinstance(asts[2], ast.IntLiteral)
    assert asts[2].value.value == 0b1     # 1        # type: ignore

def test_float_literal():
    """测试浮点数"""
    code = '3.14 0.5 123.456'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 3
    assert isinstance(asts[0], ast.FloatLiteral)
    assert asts[0].value.value == 3.14        # type: ignore
    assert isinstance(asts[1], ast.FloatLiteral)
    assert asts[1].value.value == 0.5        # type: ignore
    assert isinstance(asts[2], ast.FloatLiteral)
    assert asts[2].value.value == 123.456        # type: ignore

def test_mixed_number_formats():
    """测试混合数字格式"""
    code = '42 0x2A 0b101010 3.14'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 4
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 42        # type: ignore
    assert isinstance(asts[1], ast.IntLiteral)
    assert asts[1].value.value == 0x2A  # 42        # type: ignore
    assert isinstance(asts[2], ast.IntLiteral)
    assert asts[2].value.value == 0b101010  # 42        # type: ignore
    assert isinstance(asts[3], ast.FloatLiteral)
    assert asts[3].value.value == 3.14        # type: ignore

def test_complex_member_operations():
    """测试复杂的成员操作"""
    code = 'obj .attr .&ptr @ .method !'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 6
    assert isinstance(asts[0], ast.GetVar)
    assert asts[0].varname == 'obj'
    assert isinstance(asts[1], ast.GetAttr)
    assert asts[1].attrname == 'attr'
    assert isinstance(asts[2], ast.GetAttrPtr)
    assert asts[2].attrname == 'ptr'
    assert isinstance(asts[3], ast.KeywordOrOperator)
    assert asts[3].keyword == '@'
    assert isinstance(asts[4], ast.GetAttr)
    assert asts[4].attrname == 'method'
    assert isinstance(asts[5], ast.KeywordOrOperator)
    assert asts[5].keyword == '!'

def test_all_operators():
    """测试所有操作符"""
    code = '+ - * / ! @ . & = > < >= <= == != and or not is'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    expected_operators = ['+', '-', '*', '/', '!', '@', '.', '&', '=', '>', '<', 
                         '>=', '<=', '==', '!=', 'and', 'or', 'not', 'is']
    
    assert len(asts) == len(expected_operators)
    for i, op in enumerate(expected_operators):
        assert isinstance(asts[i], ast.KeywordOrOperator)
        assert asts[i].keyword == op        # type: ignore

def test_nested_blocks_with_numbers():
    """测试包含各种数字的嵌套代码块"""
    code = '{ { 42 0x2A 0b101010 } { 3.14 0.5 } }'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    # 外层块
    assert len(asts) == 1
    assert isinstance(asts[0], ast.CodeBlock)
    
    # 检查块结构
    assert len(blocks) == 3
    outer_block = blocks[asts[0].blockindex]
    assert len(outer_block) == 2
    assert isinstance(outer_block[0], ast.CodeBlock)
    assert isinstance(outer_block[1], ast.CodeBlock)
    
    # 第一个内层块（整数）
    inner_block_1 = blocks[outer_block[0].blockindex]
    assert len(inner_block_1) == 3
    assert isinstance(inner_block_1[0], ast.IntLiteral)
    assert inner_block_1[0].value.value == 42        # type: ignore
    assert isinstance(inner_block_1[1], ast.IntLiteral)
    assert inner_block_1[1].value.value == 0x2A        # type: ignore
    assert isinstance(inner_block_1[2], ast.IntLiteral)
    assert inner_block_1[2].value.value == 0b101010        # type: ignore
    
    # 第二个内层块（浮点数）
    inner_block_2 = blocks[outer_block[1].blockindex]
    assert len(inner_block_2) == 2
    assert isinstance(inner_block_2[0], ast.FloatLiteral)
    assert inner_block_2[0].value.value == 3.14        # type: ignore
    assert isinstance(inner_block_2[1], ast.FloatLiteral)
    assert inner_block_2[1].value.value == 0.5        # type: ignore

def test_edge_case_numbers():
    """测试边界情况的数字"""
    code = '0 0x0 0b0 0.0'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 4
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 0        # type: ignore
    assert isinstance(asts[1], ast.IntLiteral)
    assert asts[1].value.value == 0        # type: ignore
    assert isinstance(asts[2], ast.IntLiteral)
    assert asts[2].value.value == 0        # type: ignore
    assert isinstance(asts[3], ast.FloatLiteral)
    assert asts[3].value.value == 0.0        # type: ignore

def test_complex_attr_ptr_operations():
    """测试复杂的属性指针操作"""
    code = 'obj .&attr1 .attr2 ptr @ .&method1 .method2 !'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 8
    expected_types = [
        (ast.GetVar, 'obj'),
        (ast.GetAttrPtr, 'attr1'),
        (ast.GetAttr, 'attr2'),
        (ast.GetVar, 'ptr'),
        (ast.KeywordOrOperator, '@'),
        (ast.GetAttrPtr, 'method1'),
        (ast.GetAttr, 'method2'),
        (ast.KeywordOrOperator, '!')
    ]
    
    for i, (expected_type, expected_name) in enumerate(expected_types):
        assert isinstance(asts[i], expected_type)
        if hasattr(asts[i], 'attrname'):
            assert asts[i].attrname == expected_name        # type: ignore
        elif hasattr(asts[i], 'varname'):
            assert asts[i].varname == expected_name        # type: ignore
        elif hasattr(asts[i], 'keyword'):
            assert asts[i].keyword == expected_name        # type: ignore

def test_negative_numbers():
    """测试负数"""
    code = '-42 -3.14 -0x2A -0b1010'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 4
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == -42        # type: ignore
    assert isinstance(asts[1], ast.FloatLiteral)
    assert asts[1].value.value == -3.14        # type: ignore
    assert isinstance(asts[2], ast.IntLiteral)
    assert asts[2].value.value == -0x2A  # -42        # type: ignore
    assert isinstance(asts[3], ast.IntLiteral)
    assert asts[3].value.value == -0b1010  # -10        # type: ignore

def test_mixed_positive_negative():
    """测试正负数混合"""
    code = '42 -42 3.14 -3.14 + -'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 6
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 42        # type: ignore
    assert isinstance(asts[1], ast.IntLiteral)
    assert asts[1].value.value == -42        # type: ignore
    assert isinstance(asts[2], ast.FloatLiteral)
    assert asts[2].value.value == 3.14        # type: ignore
    assert isinstance(asts[3], ast.FloatLiteral)
    assert asts[3].value.value == -3.14        # type: ignore
    assert isinstance(asts[4], ast.KeywordOrOperator)
    assert asts[4].keyword == '+'
    assert isinstance(asts[5], ast.KeywordOrOperator)
    assert asts[5].keyword == '-'

def test_negative_zero():
    """测试负零"""
    code = '-0 -0.0'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 2
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 0  # -0 在整数中就是 0        # type: ignore
    assert isinstance(asts[1], ast.FloatLiteral)
    assert asts[1].value.value == -0.0        # type: ignore

def test_negative_in_blocks():
    """测试代码块中的负数"""
    code = '{ -42 &x = } { -3.14 &y = }'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    assert len(asts) == 2
    assert isinstance(asts[0], ast.CodeBlock)
    assert isinstance(asts[1], ast.CodeBlock)
    
    # 检查第一个块内容
    block1 = blocks[0]
    assert len(block1) == 3
    assert isinstance(block1[0], ast.IntLiteral)
    assert block1[0].value.value == -42        # type: ignore
    assert isinstance(block1[1], ast.GetVarPtr)
    assert block1[1].varname == 'x'
    assert isinstance(block1[2], ast.KeywordOrOperator)
    assert block1[2].keyword == '='
    
    # 检查第二个块内容
    block2 = blocks[1]
    assert len(block2) == 3
    assert isinstance(block2[0], ast.FloatLiteral)
    assert block2[0].value.value == -3.14        # type: ignore
    assert isinstance(block2[1], ast.GetVarPtr)
    assert block2[1].varname == 'y'
    assert isinstance(block2[2], ast.KeywordOrOperator)
    assert block2[2].keyword == '='

def test_complex_negative_expressions():
    """测试包含负数的复杂表达式"""
    code = '-5 3 + &result = result @ -2 *'
    tokens = tokenize(code)
    asts, blocks = parse(tokens)
    
    expected_values = [
        (ast.IntLiteral, -5),      # -5
        (ast.IntLiteral, 3),       # 3  
        (ast.KeywordOrOperator, '+'),
        (ast.GetVarPtr, 'result'),
        (ast.KeywordOrOperator, '='),
        (ast.GetVar, 'result'),
        (ast.KeywordOrOperator, '@'),
        (ast.IntLiteral, -2),      # -2
        (ast.KeywordOrOperator, '*')
    ]
    
    for i, (expected_type, expected_value) in enumerate(expected_values):
        assert isinstance(asts[i], expected_type)
        if isinstance(asts[i], (ast.IntLiteral, ast.FloatLiteral)):
            assert asts[i].value.value == expected_value        # type: ignore
        elif isinstance(asts[i], ast.GetVarPtr):
            assert asts[i].varname == expected_value        # type: ignore
        elif isinstance(asts[i], ast.GetVar):
            assert asts[i].varname == expected_value        # type: ignore
        elif isinstance(asts[i], ast.KeywordOrOperator):
            assert asts[i].keyword == expected_value        # type: ignore


# 测试重构后的辅助函数
def test_tokens_to_asts():
    """测试tokens到AST的转换函数"""
    from src.parser import tokens_to_asts
    tokens = ['42', '&x', '=', '"hello"']
    asts = tokens_to_asts(tokens)
    
    assert len(asts) == 4
    assert isinstance(asts[0], ast.IntLiteral)
    assert asts[0].value.value == 42        # type: ignore
    assert isinstance(asts[1], ast.GetVarPtr)
    assert asts[1].varname == 'x'
    assert isinstance(asts[2], ast.KeywordOrOperator)
    assert asts[2].keyword == '='
    assert isinstance(asts[3], ast.StringLiteral)
    assert asts[3].value.value == 'hello'        # type: ignore


def test_find_code_blocks():
    """测试查找代码块函数"""
    from src.parser import find_code_blocks
    tokens = ['{', '42', '&x', '=', '}']
    blocks = find_code_blocks(tokens)
    
    assert len(blocks) == 1
    assert blocks[0] == (0, 4)  # 开始索引0，结束索引4


def test_process_code_blocks():
    """测试处理代码块函数"""
    from src.parser import process_code_blocks
    # 创建一些模拟的AST节点
    ast_nodes = [ast.BaseAst(), ast.BaseAst(), ast.BaseAst(), ast.BaseAst(), ast.BaseAst()]
    block_indices = [(0, 4)]  # 一个从索引0到4的块
    
    processed_asts, block_contents = process_code_blocks(ast_nodes, block_indices)
    
    assert len(processed_asts) == 1
    assert isinstance(processed_asts[0], ast.CodeBlock)
    assert len(block_contents) == 1
    assert len(block_contents[0]) == 3  # 中间的3个节点