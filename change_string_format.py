import sys


def camelCaseFormat(input_str: str) -> str:
    """
    Преобразование входящей строки из snake_case в camelCase
    :param input_str: Входящая строка
    :return: Строка в camelCase
    """
    result: list = list()

    index: int = 0
    while index < len(input_str):
        char: str = input_str[index]
        # Если символ '_' и следующий индекс есть в строке, то добавляем следующий символ в верхнем регистре
        if (char == '_') and ((index + 1) < len(input_str)):
            index += 1
            char = input_str[index]
            result.append(char.upper())
        else:
            result.append(char)

        index += 1
    return "".join(result)


def snake_case_format(input_str: str) -> str:
    """
    Преобразование входящей строки из camelCase в snake_case
    :param input_str: Входящая строка
    :return: Строка в snake_case
    """
    result: list = list()

    for char in input_str:
        # Если символ в верхнем регистре, добавляем в строку символ '_' и текущий символ в нижнем регистре
        if char.isupper():
            result.append('_')
            result.append(char.lower())
        else:
            result.append(char)

    return "".join(result)


def reversed_format(input_str: str) -> str:
    """
    Изменяет формат строки с camelCase на snake_case и обратно.
    :param input_str: Строка, содержащая текст в camelCase или snake_case
    :return: Строка в camelCase или snake_case
    :raise ValueError В случае смешения форматов и без указания конкретного целевого формата
    """
    isCamelCase: bool = False
    is_snake_case: bool = False

    result: list = list()

    index: int = 0
    while index < len(input_str):
        char: str = input_str[index]
        # Если символ '_' и следующий индекс есть в строке, то добавляем следующий символ в верхнем регистре
        if (char == '_') and ((index + 1) < len(input_str)):
            index += 1
            char = input_str[index]
            result.append(char.upper())
            is_snake_case = True
        # Если символ в верхнем регистре, добавляем в строку символ '_' и текущий символ в нижнем регистре
        elif char.isupper():
            result.append('_')
            result.append(char.lower())
            isCamelCase = True
        else:
            result.append(char)

        if isCamelCase and is_snake_case:
            raise ValueError("Input string must be in camelCase or snake_case only")

        index += 1
    return "".join(result)


def reformat(input_str: str, target_format: str = "reversed") -> str:
    """
    Изменяет формат строки с camelCase на snake_case и обратно.
    :param input_str: Строка, содержащая текст в camelCase или snake_case
    :param target_format: Целевой формат конвертации. Доступные значения 'snake_case' или 'camelCase', в ином случае
    применяется обратное преобразование
    :return: Строка в camelCase или snake_case
    :raise ValueError В случае смешения форматов и без указания конкретного целевого формата
    """

    if target_format == "camelCase":
        return camelCaseFormat(input_str)
    elif target_format == "snake_case":
        return snake_case_format(input_str)
    else:
        return reversed_format(input_str)


input_str = None
format_to = None

if len(sys.argv) > 2:
    input_str = sys.argv[1]
    format_to = sys.argv[2]
elif len(sys.argv) > 1:
    input_str = sys.argv[1]

if not input_str:
    input_str = input("Input string in camelCase or snake_case: ")
    format_to = input("Input target format: ")

print(reformat(input_str, format_to))
