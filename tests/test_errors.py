import sys
import os
import pytest

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.errors import ReverError, ReverSyntaxError, ReverUnicodeError, ErrorDurationType

def test_rever_error_default():
    """测试默认的 ReverError"""
    error = ReverError("test message")
    assert str(error) == "ReverError - ReverError cause during RUN: test message"
    assert error.error_duration == ErrorDurationType.RUN

def test_rever_error_with_start_duration():
    """测试指定 START 类型的 ReverError"""
    error = ReverError("test message", error_duration=ErrorDurationType.START)
    assert str(error) == "ReverError - ReverError cause during START: test message"
    assert error.error_duration == ErrorDurationType.START

def test_rever_error_without_message():
    """测试没有消息的 ReverError"""
    error = ReverError()
    assert str(error) == "ReverError - ReverError cause during RUN"

def test_rever_syntax_error():
    """测试 ReverSyntaxError"""
    error = ReverSyntaxError("syntax error")
    assert str(error) == "ReverError - ReverSyntaxError cause during START: syntax error"
    assert error.error_duration == ErrorDurationType.START

def test_rever_unicode_error():
    """测试 ReverUnicodeError"""
    error = ReverUnicodeError("unicode error")
    assert str(error) == "ReverError - ReverUnicodeError cause during START: unicode error"
    assert error.error_duration == ErrorDurationType.START

def test_error_duration_type_enum():
    """测试 ErrorDurationType 枚举"""
    assert ErrorDurationType.START.value == 1
    assert ErrorDurationType.RUN.value == 2
    assert ErrorDurationType.START.name == "START"
    assert ErrorDurationType.RUN.name == "RUN"

def test_rever_error_with_multiple_args():
    """测试带有多个参数的 ReverError"""
    error = ReverError("error", "with", "multiple", "args")
    assert str(error) == "ReverError - ReverError cause during RUN: errorwithmultipleargs"

def test_rever_error_inheritance():
    """测试 ReverError 的继承关系"""
    error = ReverError()
    assert isinstance(error, Exception)
    
    syntax_error = ReverSyntaxError()
    assert isinstance(syntax_error, ReverError)
    assert isinstance(syntax_error, Exception)
    
    unicode_error = ReverUnicodeError()
    assert isinstance(unicode_error, ReverError)
    assert isinstance(unicode_error, Exception)