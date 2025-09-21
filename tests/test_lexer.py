import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.lexer import tokenize, process_escapes

class TestLexer(unittest.TestCase):

    def test_process_escapes(self):
        self.assertEqual(process_escapes('"hello\\nworld"'), '"hello\nworld"')
        self.assertEqual(process_escapes('"hello\\t\\"there\\""'), '"hello\t\"there\""')
        self.assertEqual(process_escapes('"no escape"'), '"no escape"')
        self.assertEqual(process_escapes('"unclosed'), '"unclosed')  # 未闭合字符串

    def test_basic_tokens(self):
        code = '42 &x ='
        tokens = tokenize(code)
        self.assertEqual(tokens, ['42', '&x', '='])

    def test_string_literal(self):
        code = '"hello" "world" + &greeting ='
        tokens = tokenize(code)
        self.assertEqual(tokens, ['"hello"', '"world"', '+', '&greeting', '='])

    def test_escaped_string(self):
        code = '"hello\\nworld" print !'
        tokens = tokenize(code)
        self.assertEqual(tokens, ['"hello\nworld"', 'print', '!'])

    def test_line_comment(self):
        code = '''
        # 这是一行注释
        42 &x = # 赋值
        '''
        tokens = tokenize(code)
        self.assertEqual(tokens, ['42', '&x', '='])

    def test_block_comment(self):
        code = '''
        ##
        这是块注释
        可以多行
        ##
        42 &x =
        '''
        tokens = tokenize(code)
        self.assertEqual(tokens, ['42', '&x', '='])

    def test_nested_block_comment(self):
        code = '''
        ##
        外层注释
        # 这里不是结束
        继续注释
        ##
        42 &x =
        '''
        tokens = tokenize(code)
        self.assertEqual(tokens, ['42', '&x', '='])

    def test_code_block(self):
        code = '{&x = x 1 + return } &inc ='
        tokens = tokenize(code)
        self.assertEqual(tokens, ['{', '&x', '=', 'x', '1', '+', 'return', '}', '&inc', '='])

    def test_mixed_whitespace(self):
        code = '  42   &x  =  '
        tokens = tokenize(code)
        self.assertEqual(tokens, ['42', '&x', '='])

    def test_unclosed_string(self):
        code = '"hello world'
        tokens = tokenize(code)
        self.assertEqual(tokens, ['"hello world'])

    def test_empty_input(self):
        self.assertEqual(tokenize(''), [])
        self.assertEqual(tokenize('   '), [])
        self.assertEqual(tokenize('## comment ##'), [])

    def test_comment_only(self):
        code = '# just a comment\n## block ##'
        self.assertEqual(tokenize(code), [])

if __name__ == '__main__':
    unittest.main()