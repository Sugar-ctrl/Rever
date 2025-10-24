import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lexer import tokenize

def test_basic_tokens():
    code = '42 &x ='
    tokens = tokenize(code)
    assert tokens == ['42', '&x', '=']

def test_string_literal():
    code = '"hello" "world" + &greeting ='
    tokens = tokenize(code)
    assert tokens == ['"hello"', '"world"', '+', '&greeting', '=']

def test_escaped_string():
    code = '"hello\nworld" print !'
    tokens = tokenize(code)
    assert tokens == ['"hello\nworld"', 'print', '!']

def test_line_comment():
    code = '''
    # 这是一行注释
    42 &x = # 赋值
    '''
    tokens = tokenize(code)
    assert tokens == ['42', '&x', '=']

def test_block_comment():
    code = '''
    ##
    这是块注释
    可以多行
    ##
    42 &x ='''
    tokens = tokenize(code)
    assert tokens == ['42', '&x', '=']

def test_nested_block_comment():
    code = '''
    ##
    外层注释
    # 这里不是结束
    继续注释
    ##
    42 &x ='''
    tokens = tokenize(code)
    assert tokens == ['42', '&x', '=']

def test_code_block():
    code = '{&x = x 1 + return } &inc ='
    tokens = tokenize(code)
    assert tokens == ['{', '&x', '=', 'x', '1', '+', 'return', '}', '&inc', '=']

def test_mixed_whitespace():
    code = '  42   &x  =  '
    tokens = tokenize(code)
    assert tokens == ['42', '&x', '=']

def test_unclosed_string():
    code = '"hello world'
    tokens = tokenize(code)
    assert tokens == ['"hello world']

def test_empty_input():
    assert tokenize('') == []
    assert tokenize('   ') == []
    assert tokenize('## comment ##') == []

def test_comment_only():
    code = '# just a comment\n## block ##'
    assert tokenize(code) == []


# 测试重构后的辅助函数
def test_handle_string():
    """测试字符串处理函数"""
    from src.lexer import handle_string
    tokens = []
    # 测试正常字符串
    result_index = handle_string('"hello world"', 0, tokens)
    assert result_index == 13  # "hello world" 长度 + 1
    assert tokens == ['"hello world"']
    
    # 测试转义字符串
    tokens = []
    result_index = handle_string('"hello\nworld"', 0, tokens)
    assert result_index == 13  # "hello\nworld" 长度 + 1
    assert tokens == ['"hello\nworld"']
    
    # 测试未闭合字符串
    tokens = []
    result_index = handle_string('"unclosed string', 0, tokens)
    assert result_index == 17  # "unclosed string" 长度 + 1 (包括末尾)
    assert tokens == ['"unclosed string']


def test_handle_block_comment():
    """测试块注释处理函数"""
    from src.lexer import handle_block_comment
    # 测试处理块注释，应该跳转到结束标记
    index = handle_block_comment('## comment ##', 0)
    assert index == 13  # 跳转到 ## 结束标记之后的位置


def test_handle_line_comment():
    """测试行注释处理函数"""
    from src.lexer import handle_line_comment
    # 测试处理行注释，应该跳转到行尾
    index = handle_line_comment('# comment\nnext line', 0)
    assert index == 9  # 跳转到换行符位置


def test_handle_special_chars():
    """测试特殊字符处理函数"""
    from src.lexer import handle_special_chars
    tokens = []
    # 测试空格
    index, handled = handle_special_chars('   ', 0, tokens)
    assert index == 1
    assert handled == True
    assert tokens == []
    
    # 测试大括号
    tokens = []
    index, handled = handle_special_chars('{', 0, tokens)
    assert index == 1
    assert handled == True
    assert tokens == ['{']
    
    # 测试普通字符
    tokens = []
    index, handled = handle_special_chars('a', 0, tokens)
    assert index == 0
    assert handled == False
    assert tokens == []


def test_handle_token():
    """测试普通token处理函数"""
    from src.lexer import handle_token
    tokens = []
    # 测试简单token
    index = handle_token('variable name', 0, tokens)
    assert index == 8  # 'variable' 的长度
    assert tokens == ['variable']
    
    # 测试数字token
    tokens = []
    index = handle_token('42 +', 0, tokens)
    assert index == 2  # '42' 的长度
    assert tokens == ['42']