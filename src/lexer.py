def tokenize(code: str) -> list[str]:
    '''
    词法分析器
    :param code: 输入的代码字符串
    :return: 词法分析结果，即 token 列表
    '''
    # 初始化变量
    current_index: int = 0
    tokens: list[str] = []
    block_comment_flag: bool = False
    line_comment_flag: bool = False
    while current_index < len(code):
        # 处理字符串
        if code[current_index] == '"':
            start_index: int = current_index
            current_index += 1
            while (
                current_index < len(code)
                and not (
                    code[current_index] == '"'
                    and code[current_index-1] != '\\'
                    )
                ):
                current_index += 1

            if (current_index < len(code)
                    and code[current_index] == '"'):
                tokens.append(
                    code[start_index:current_index+1]
                )
            else:
                # 未闭合字符串，保留原始字符串
                tokens.append(code[start_index:current_index+1])

            current_index += 1
            continue

        # 处理块注释
        if code[current_index:current_index+2] == '##':
            block_comment_flag = not block_comment_flag
            current_index += 2
            continue
        if block_comment_flag:
            current_index += 1
            continue

        # 处理行注释
        if code[current_index] == '#':
            line_comment_flag = True
            current_index += 1
            continue
        if code[current_index] == '\n':
            line_comment_flag = False
            current_index += 1
            continue
        if line_comment_flag:
            current_index += 1
            continue

        # 跳过空格
        if code[current_index].isspace():
            current_index += 1
            continue

        # 处理{}包括的代码块
        if code[current_index] in ['{', '}']:
            tokens.append(code[current_index])
            current_index += 1
            continue

        # 此时必然是一个 token 的开始
        token_start_index: int = current_index
        while (current_index < len(code)
               and not code[current_index].isspace()):
            current_index += 1
        tokens.append(code[token_start_index:current_index])

    # 返回tokens列表
    return tokens
