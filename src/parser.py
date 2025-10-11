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


def parse(tokens: list[str]) -> tuple[list[ast.BaseAst], list[list[ast.BaseAst]]]:
    """
    解析tokens列表
    :param tokens: 待解析的tokens列表
    :return: 解析后的asts列表和block_content列表
    """
    asts_non_block: list[ast.BaseAst] = []
    
    # 第一步：将 tokens 转换为基本 AST 节点
    for i in tokens:
        if i in ['{', '}']:
            asts_non_block.append(ast.BaseAst()) # 占位符
            continue

        if i in ['+', '-', '*', '/',
                 '!', '@', '.', '&', '=',
                 '>', '<', '>=', '<=', '==', '!=',
                 'and', 'or', 'not', 'is']:
            asts_non_block.append(
                ast.KeywordOrOperator(keyword=i)
            )
            continue

        if i in ['true', 'false']:
            asts_non_block.append(
                ast.BooleanLiteral(value=(i == 'true'))
            )
            continue

        if i == 'null':
            asts_non_block.append(
                ast.NullLiteral()
            )
            continue

        if re.match(r'^\.[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetAttr(attrname=i[1:])
            )
            continue

        if re.match(r'^\.&[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetAttrPtr(attrname=i[2:])
            )
            continue

        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetVar(varname=i)
            )
            continue

        if re.match(r'^&[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetVarPtr(varname=i[1:])
            )
            continue

        if re.match(r'^\-?[0-9]+$', i):
            asts_non_block.append(
                ast.IntLiteral(value=int(i))
            )
            continue

        if re.match(r'^\-?0x[0-9a-fA-F]+$', i):
            asts_non_block.append(
                ast.IntLiteral(value=int(i, 16))
            )
            continue

        if re.match(r'^\-?0b[01]+$', i):
            asts_non_block.append(
                ast.IntLiteral(value=int(i, 2))
            )
            continue

        if i[0] == i[-1] == '"':
            asts_non_block.append(
                ast.StringLiteral(value=process_string_escapes(i))
            )
            continue

        if re.match(r'^\-?[0-9]+(\.[0-9]+)?$', i):
            asts_non_block.append(
                ast.FloatLiteral(value=float(i))
            )
            continue

        raise SyntaxError(f"Unknown token: {i}") # TODO:以后应调用rever的错误处理

    # 第二步：找出其中的所有代码块范围
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

    # 第三步：根据代码块范围，把代码块中的内容打包放进block_content_with_space
    # 同时，在asts_with_space中用CodeBlock以及None占位符替换代码块内容
    block_content_with_space: list[list[ast.BaseAst|None]] = []
    asts_with_space: list[ast.BaseAst|None] = asts_non_block.copy()
    for index, (start, end) in enumerate(block_index):
        block_content_with_space.append(asts_with_space[start+1:end])
        asts_with_space[start] = ast.CodeBlock(index)
        asts_with_space[start+1:end+1] = [None] * (end - start)

    # 第四步：把asts_with_space中的None占位符去掉，得到最终的asts列表
    asts: list[ast.BaseAst] = []
    for i in asts_with_space:
        if i is None:
            continue
        else:
            asts.append(i)

    # 第五步：把block_content_with_space中的None占位符去掉，得到最终的block_content列表
    block_content: list[ast.BaseAst] = []
    for i in block_content_with_space:
        tmp: list[ast.BaseAst] = []
        for j in i:
            if j is None:
                continue
            else:
                tmp.append(j)
        block_content.append(tmp)

    return asts, block_content