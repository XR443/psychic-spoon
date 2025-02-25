def get_numeric_or_empty_string(label: str, **constraints) -> str:
    """
    Функция получения пустой строки или строки, состоящей из цифр
    :param label: Заголовок для ввода
    :param constraints: Ограничения для вводимого поля:
                        min - минимальное значение, включая
                        max - максимальное значение, включая
                        target_length - до какой длины строки дополнять
    :return: Пустую строку или строку, содержащую цифры
    """
    input_str = input(label)

    min_constraint = None
    if "min" in constraints:
        min_constraint = constraints["min"]

    max_constraint = None
    if "max" in constraints:
        max_constraint = constraints["max"]

    # Если введенная строка не пустая и содержит не числа
    while (input_str and not input_str.isnumeric() or
           not (  # или числа не входят в диапазон, если существуют ограничения
                   (not min_constraint or min_constraint <= int(input_str))
                   and
                   (not max_constraint or int(input_str) <= max_constraint)
           )):
        input_str = input(label)

    if "target_length" in constraints:
        target_length: int = constraints["target_length"]
        input_str = input_str.zfill(target_length)

    return input_str


def get_capitalize_value_or_empty_string(label: str) -> str:
    """
    Функция получения пустой строки или строки, состоящей из алфавитных символов написанных с заглавной буквы
    :param label: Заголовок для ввода
    :return: Пустую строку или строку, содержащую цифры
    """
    input_str = input(label)
    while input_str and not input_str.isalpha():
        input_str = input(label)

    return input_str.capitalize()


def print_db(db: dict, column_length: int = 15):
    """
    Печатает словарь в виде таблицы
    :param db: Словарь:
                ключ - строка
                значение - словарь:
                            name - строка
                            surname - строка
                            age - целое число
    :param column_length: Размер колонки, в символах
    :return: -
    """
    modifier = "".join(["{: <", str(column_length), "}"])
    print(f"{modifier.format('Ид')}|{modifier.format('Фамилия')}|{modifier.format('Имя')}|{modifier.format('Возраст')}")
    for user_id, user_data in db.items():
        user_id_str = modifier.format(user_id)
        user_surname = modifier.format(user_data["surname"])
        user_name = modifier.format(user_data["name"])
        user_age = modifier.format(user_data["age"])
        print(f"{user_id_str}|{user_surname}|{user_name}|{user_age}")


def get_table_data() -> dict:
    mock_db: dict = dict()

    while True:
        print("Ввод пользователя")

        input_name: str = get_capitalize_value_or_empty_string("Input user name: ")
        if not input_name:
            break

        input_surname: str = get_capitalize_value_or_empty_string("Input user surname: ")
        if not input_surname:
            break

        input_age: str = get_numeric_or_empty_string("Input user age: ", min=18, max=60)
        if not input_age:
            break

        input_id: str = get_numeric_or_empty_string("Input user id: ", target_length=8)
        if not input_id:
            break

        if input_id in mock_db:
            print(f"Person with {input_id} already in db")
        else:
            mock_db[input_id] = {"name": input_name, "surname": input_surname, "age": input_age}
    
    return mock_db
