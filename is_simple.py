import sys


def is_completely_divided_by_first_any_simple_nums(number: int) -> bool:
    """
    Проверяет делимость числа на простые одноразрядные числа
    :param number: Число для проверки
    :return: True если число делится нацело на любое одноразрядное простое число, иначе False
    """
    for simple in [2, 3, 5, 7]:
        if number % simple == 0:
            return False
    else:
        return True


def is_simple(number: int) -> bool:
    """
    Функция проверки числа на простоту. Если число делится только на себя и единицу, то оно является простым
    :param number: Число для проверки
    :return: True если число простое, иначе False
    """
    # Единица и числа меньше нуля не являются простыми
    if number <= 1:
        return False
    # Если число входит в одноразрядные простые числа, то оно простое
    elif number in [2, 3, 5, 7]:
        return True
    # Если число делится нацело на любое одноразрядное простое число, то оно не простое
    elif is_completely_divided_by_first_any_simple_nums(number):
        return True
    else:
        return False


input_number = None

if len(sys.argv) > 1:
    input_number = int(sys.argv[1])

if not input_number:
    input_number = int(input("Input number: "))

print(is_simple(input_number))
