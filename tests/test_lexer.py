import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lexer import tokenize, process_escapes

def test_process_escapes():
    assert process_escapes('"hello\\nworld"') == '"hello\nworld"'
    assert process_escapes('"hello\\t\\"there\\""') == '"hello\t\"there\""'
    assert process_escapes('"no escape"') == '"no escape"'
    assert process_escapes('"unclosed') == '"unclosed'  # 未闭合字符串

def test_basic_tokens():
    code = '42 &x ='
    tokens = tokenize(code)
    assert tokens == ['42', '&x', '=']

def test_string_literal():
    code = '"hello" "world" + &greeting ='
    tokens = tokenize(code)
    assert tokens == ['"hello"', '"world"', '+', '&greeting', '=']

def test_escaped_string():
    code = '"hello\\nworld" print !'
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