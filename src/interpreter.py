import ast_types as ast
from src.errors import *
import src.runtime.memory as mem

class Interpreter:
    def __init__(self):
        self.command_stack: list[ast.BaseAst] = []
        self.root_memory: mem.Memory = mem.Memory()

    def interpret(self, asts: list[ast.BaseAst], func_content: list[list[ast.BaseAst]]):
        """
        解释执行 AST 节点
        :param asts: 待解释执行的 AST 节点列表
        :param func_content: 函数体内容
        """
        self.command_stack = []
        for node in asts[::-1]:
            self.command_stack.append(node)
        while self.command_stack:
            node = self.command_stack.pop()
            if isinstance(node, ast.BaseAst):
                self.interpret_node(node, func_content)
            else:
                print(f"Warning: Unknown AST node type {type(node)}")

    def interpret_node(self, node: ast.BaseAst, func_content: list[list[ast.BaseAst]]):
        """
        解释执行单个 AST 节点
        :param node: 待解释执行的 AST 节点
        :param func_content: 函数体内容
        """
        {
            ast.GetAttr: self.interpret_getattr,
            ast.GetAttrPtr: self.interpret_getattrptr,
            ast.GetVar: self.interpret_getvar,
            ast.GetVarPtr: self.interpret_getvarptr,
            ast.Literal: self.interpret_literal,
            ast.KeywordOrOperator: self.interpret_keywordoroperator,
            ast.CodeBlock: self.interpret_codeblock
        }[type(node)](node, func_content)
        
    def interpret_getattr(self, node: ast.GetAttr, func_content: list[list[ast.BaseAst]]):
        """
        解释执行获取属性节点
        :param node: GetAttr 节点
        :param func_content: 函数体内容
        """
        obj = self.root_memory.pop()
        attr = node.attrname
        if attr not in obj.attrs:
            raise ReverAttributeError(f"Object of type {type(obj).__name__} has no attribute {attr}")
        self.root_memory.push(obj.attrs[attr])
        
    def interpret_getattrptr(self, node: ast.GetAttrPtr, func_content: list[list[ast.BaseAst]]):
        """
        解释执行获取属性指针节点
        :param node: GetAttrPtr 节点
        :param func_content: 函数体内容
        """
        obj = self.root_memory.pop()
        attr = node.attrname
        if attr not in obj.attrs:
            raise ReverAttributeError(f"Object of type {type(obj).__name__} has no attribute {attr}")
        self.root_memory.push(obj.attrs[attr].ptr)
        
    def interpret_getvar(self, node: ast.GetVar, func_content: list[list[ast.BaseAst]]):
        """
        解释执行获取变量节点
        :param node: GetVar 节点
        :param func_content: 函数体内容
        """
        varname = node.varname
        if varname not in self.root_memory.vars:
            raise ReverNameError(f"Variable {varname} is not defined")
        self.root_memory.push(self.root_memory.vars[varname])
        
    def interpret_getvarptr(self, node: ast.GetVarPtr, func_content: list[list[ast.BaseAst]]):
        """
        解释执行获取变量指针节点
        :param node: GetVarPtr 节点
        :param func_content: 函数体内容
        """
        varname = node.varname
        if varname not in self.root_memory.vars:
            raise ReverNameError(f"Variable {varname} is not defined")
        self.root_memory.push(self.root_memory.vars[varname].ptr)
        
    def interpret_literal(self, node: ast.Literal, func_content: list[list[ast.BaseAst]]):
        """
        解释执行字面量节点
        :param node: Literal 节点
        :param func_content: 函数体内容
        """
        self.root_memory.push(node.value)
        
    def interpret_keywordoroperator(self, node: ast.KeywordOrOperator, func_content: list[list[ast.BaseAst]]):
        """
        解释执行关键字或运算符节点
        :param node: KeywordOrOperator 节点
        :param func_content: 函数体内容
        """
        pass
        
    def interpret_codeblock(self, node: ast.CodeBlock, func_content: list[list[ast.BaseAst]]):
        """
        解释执行代码块节点
        :param node: CodeBlock 节点
        :param func_content: 函数体内容
        """
        self.command_stack.extend(func_content[node.blockindex])
