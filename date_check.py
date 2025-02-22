import sys

month_to_days: dict = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}


def is_leap_year(year: int) -> bool:
    """
    Введенный год високосный или нет
    :param year: Год в формате yyyy
    :return: True если год високосный, иначе False
    """
    return (((year % 4) == 0) and not ((year % 100) == 0)) or ((year % 400) == 0)


def validate_date(str_date: str) -> bool:
    """
    Проверяет существование введенной даты.
    :param str_date: Дата строкой в формате dd.mm.yyyy
    :return: True если дата валидна, иначе False
    """
    day_str, month_str, year_str = str_date.split('.')

    day: int = int(day_str)
    month: int = int(month_str)
    year: int = int(year_str)

    if month_to_days[month] < day:
        if is_leap_year(year) and month == 2 and day <= 29:
            return True
        else:
            return False
    else:
        return True


input_str = None

if len(sys.argv) > 1:
    input_str = sys.argv[1]

if not input_str:
    input_str = input("Input date with in format 'dd.mm.yyyy': ")

print(validate_date(input_str))