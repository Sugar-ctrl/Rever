import src.ast_types as ast
import re


def process_string_escapes(s: str) -> str:
    """
    处理字符串中的转义序列（沿用Python规则）
    """
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        inner = s[1:-1]
        try:
            processed = inner.encode().decode('unicode_escape')
            return processed
        except UnicodeDecodeError:
            print(f"Warning: Unescaped quote in string literal: {s}")
            return inner
    # 处理未闭合字符串
    if len(s) >= 1 and s[0] == '"':
        return s[1:]
    return s


def tokens_to_asts(tokens: list[str]) -> list[ast.BaseAst]:
    """
    将 tokens 转换为基本 AST 节点
    :param tokens: 待转换的tokens列表
    :return: 转换后的AST节点列表
    """
    asts: list[ast.BaseAst] = []
    
    for token in tokens:
        if token in ['{', '}']:
            asts.append(ast.BaseAst()) # 占位符
            continue

        if token in ['+', '-', '*', '/',
                     '!', '@', '.', '&', '=',
                     '>', '<', '>=', '<=', '==', '!=',
                     'and', 'or', 'not', 'is']:
            asts.append(
                ast.KeywordOrOperator(keyword=token)
            )
            continue

        if token in ['true', 'false']:
            asts.append(
                ast.BooleanLiteral(value=(token == 'true'))
            )
            continue

        if token == 'null':
            asts.append(
                ast.NullLiteral()
            )
            continue

        if re.match(r'^\.[a-zA-Z_][a-zA-Z0-9_]*$', token):
            asts.append(
                ast.GetAttr(attrname=token[1:])
            )
            continue

        if re.match(r'^\.&[a-zA-Z_][a-zA-Z0-9_]*$', token):
            asts.append(
                ast.GetAttrPtr(attrname=token[2:])
            )
            continue

        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
            asts.append(
                ast.GetVar(varname=token)
            )
            continue

        if re.match(r'^&[a-zA-Z_][a-zA-Z0-9_]*$', token):
            asts.append(
                ast.GetVarPtr(varname=token[1:])
            )
            continue

        if re.match(r'^\-?[0-9]+$', token):
            asts.append(
                ast.IntLiteral(value=int(token))
            )
            continue

        if re.match(r'^\-?0x[0-9a-fA-F]+$', token):
            asts.append(
                ast.IntLiteral(value=int(token, 16))
            )
            continue

        if re.match(r'^\-?0b[01]+$', token):
            asts.append(
                ast.IntLiteral(value=int(token, 2))
            )
            continue

        if token[0] == token[-1] == '"':
            asts.append(
                ast.StringLiteral(value=process_string_escapes(token))
            )
            continue

        if re.match(r'^\-?[0-9]+(\.[0-9]+)?$', token):
            asts.append(
                ast.FloatLiteral(value=float(token))
            )
            continue

        raise SyntaxError(f"Unknown token: {token}") # TODO:以后应调用rever的错误处理
        
    return asts


def find_code_blocks(tokens: list[str]) -> list[tuple[int, int]]:
    """
    找出其中的所有代码块范围
    :param tokens: tokens列表
    :return: 代码块范围列表
    """
    block_start_index_tmp: list[int] = []
    block_index: list[tuple[int, int]] = []

    for index, token in enumerate(tokens):
        if token == '{':
            block_start_index_tmp.append(index)
        elif token == '}':
            if len(block_start_index_tmp) == 0:
                raise SyntaxError("Unmatched '}'") # TODO:以后应调用rever的错误处理
            block_index.append((block_start_index_tmp.pop(), index))
    if len(block_start_index_tmp) != 0:
        raise SyntaxError("Unmatched '{'") # TODO:以后应调用rever的错误处理
        
    return block_index


def process_code_blocks(asts: list[ast.BaseAst], block_index: list[tuple[int, int]]) -> tuple[list[ast.BaseAst], list[list[ast.BaseAst]]]:
    """
    处理代码块内容
    :param asts: AST节点列表
    :param block_index: 代码块范围列表
    :return: 处理后的AST节点列表和代码块内容列表
    """
    # 根据代码块范围，把代码块中的内容打包放进block_content_with_space
    # 同时，在asts_with_space中用CodeBlock以及None占位符替换代码块内容
    block_content_with_space: list[list[ast.BaseAst|None]] = []
    asts_with_space: list[ast.BaseAst|None] = asts.copy()
    for index, (start, end) in enumerate(block_index):
        block_content_with_space.append(asts_with_space[start+1:end])
        asts_with_space[start] = ast.CodeBlock(index)
        asts_with_space[start+1:end+1] = [None] * (end - start)

    # 把asts_with_space中的None占位符去掉，得到最终的asts列表
    final_asts: list[ast.BaseAst] = []
    for node in asts_with_space:
        if node is not None:
            final_asts.append(node)

    # 把block_content_with_space中的None占位符去掉，得到最终的block_content列表
    block_content: list[list[ast.BaseAst]] = []
    for block in block_content_with_space:
        tmp: list[ast.BaseAst] = []
        for node in block:
            if node is not None:
                tmp.append(node)
        block_content.append(tmp)

    return final_asts, block_content


def parse(tokens: list[str]) -> tuple[list[ast.BaseAst], list[list[ast.BaseAst]]]:
    """
    解析tokens列表
    :param tokens: 待解析的tokens列表
    :return: 解析后的asts列表和block_content列表
    """
    # 第一步：将 tokens 转换为基本 AST 节点
    asts_non_block = tokens_to_asts(tokens)
    
    # 第二步：找出其中的所有代码块范围
    block_index = find_code_blocks(tokens)

    # 第三步：处理代码块内容
    asts, block_content = process_code_blocks(asts_non_block, block_index)

    return asts, block_content