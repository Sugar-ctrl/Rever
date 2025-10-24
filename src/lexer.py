def handle_string(code: str, current_index: int, tokens: list[str]) -> int:
    '''
    处理字符串字面量
    :param code: 输入的代码字符串
    :param current_index: 当前索引
    :param tokens: token列表
    :return: 处理后的索引
    '''
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

    return current_index + 1


def handle_block_comment(code: str, current_index: int) -> int:
    '''
    处理块注释
    :param code: 输入的代码字符串
    :param current_index: 当前索引
    :return: 处理后的索引
    '''
    current_index += 2
    while (
        current_index < len(code)
        and not (
            code[current_index:current_index+2] == '##'
            )
        ):
        current_index += 1
    current_index += 2
    return current_index


def handle_line_comment(code: str, current_index: int) -> int:
    '''
    处理行注释
    :param code: 输入的代码字符串
    :param current_index: 当前索引
    :return: 处理后的索引
    '''
    current_index += 2
    while (
        current_index < len(code)
        and code[current_index] != '\n'
    ):
        current_index += 1
    return current_index


def handle_special_chars(code: str, current_index: int, tokens: list[str]) -> tuple[int, bool]:
    '''
    处理特殊字符
    :param code: 输入的代码字符串
    :param current_index: 当前索引
    :param tokens: token列表
    :return: 处理后的索引和是否处理了特殊字符
    '''
    # 确保索引不超出范围
    if current_index >= len(code):
        return current_index, False
        
    # 处理空格
    if code[current_index].isspace():
        return current_index + 1, True

    # 处理{}包括的代码块
    if code[current_index] in ['{', '}']:
        tokens.append(code[current_index])
        return current_index + 1, True

    return current_index, False


def handle_token(code: str, current_index: int, tokens: list[str]) -> int:
    '''
    处理普通token
    :param code: 输入的代码字符串
    :param current_index: 当前索引
    :param tokens: token列表
    :return: 处理后的索引
    '''
    # 此时必然是一个 token 的开始
    token_start_index: int = current_index
    while (current_index < len(code)
           and not code[current_index].isspace()):
        current_index += 1
    tokens.append(code[token_start_index:current_index])
    return current_index


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
            current_index = handle_string(code, current_index, tokens)
            continue

        # 处理块注释
        if code[current_index:current_index+2] == '##':
            current_index = handle_block_comment(code, current_index)
            continue

        # 处理行注释
        if code[current_index] == '#':
            current_index = handle_line_comment(code, current_index)
            continue

        # 处理特殊字符
        current_index, special_char_flag = handle_special_chars(code, current_index, tokens)
        if special_char_flag:
            continue

        # 此时必然是一个 token 的开始
        current_index = handle_token(code, current_index, tokens)

    # 返回tokens列表
    return tokens
