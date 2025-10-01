import src.ast_types as ast
import re


def parse(tokens: list[str]) -> tuple[list[ast.BaseAst], list[list[ast.BaseAst]]]:
    """
    解析tokens列表
    :param tokens: 待解析的tokens列表
    :return: 解析后的asts列表和block_content列表
    """
    asts_non_block: list[ast.BaseAst] = []
    for i in tokens:
        if i in ['{', '}']:
            continue

        if re.match(r'^\.[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetAttr(attr_name=i[1:])
            )
            continue

        if re.match(r'^\.&[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetAttrPtr(attr_name=i[2:])
            )
            continue

        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetVar(var_name=i)
            )
            continue

        if re.match(r'^&[a-zA-Z_][a-zA-Z0-9_]*$', i):
            asts_non_block.append(
                ast.GetVarPtr(var_name=i[1:])
            )
            continue

        if re.match(r'^[0-9]+$', i):
            asts_non_block.append(
                ast.IntLiteral(value=int(i))
            )
            continue

        if re.match(r'^0x[0-9a-fA-F]+$', i):
            asts_non_block.append(
                ast.IntLiteral(value=int(i, 16))
            )
            continue

        if re.match(r'^0b[01]+$', i):
            asts_non_block.append(
                ast.IntLiteral(value=int(i, 2))
            )
            continue

        if i[0] == i[-1] == '"':
            asts_non_block.append(
                ast.StringLiteral(value=i[1:-1])
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
    
        if re.match(r'^[0-9]+(\.[0-9]+)?$', i):
            asts_non_block.append(
                ast.FloatLiteral(value=float(i))
            )
            continue

        # TODO:整理好关键字运算符的列表后，在这里判断是否是关键字或运算符
        raise SyntaxError(f"Unknown token: {i}") # TODO:以后应调用rever的错误处理

    block_start_index_tmp: list[int] = []
    block_index: list[tuple[int, int]] = []

    for index, token in enumerate(tokens):
        if token == '{':
            block_start_index_tmp.append(index)
        elif token == '}':
            if len(block_start_index_tmp) == 0:
                raise SyntaxError("Unmatched '}'") # TODO:以后应调用rever的错误处理
            block_index.append((block_start_index_tmp.pop(), index))
    
    block_content_with_space: list[list[ast.BaseAst|None]] = []
    asts_with_space: list[ast.BaseAst|None] = asts_non_block.copy()
    for start, end in block_index:
        block_content_with_space.append(asts_with_space[start+1:end])
        asts_with_space[start] = ast.CodeBlock(index)
        asts_with_space[start+1:end] = [None] * (end - start - 1)

    asts: list[ast.BaseAst] = []
    for i in asts_with_space:
        if i is None:
            continue
        else:
            asts.append(i)

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