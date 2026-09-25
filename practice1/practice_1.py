import datetime
from datetime import date

# Словарь день недели в именование
weekdays = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

# Словарь паттернов числовых символов
patterns = {
    '0': [" *** ",
          "*   *",
          "*   *",
          "*   *",
          " *** "],

    '1': ["  *  ",
          " **  ",
          "  *  ",
          "  *  ",
          " *** "],

    '2': [" *** ",
          "*   *",
          "   * ",
          "  *  ",
          "*****"],

    '3': [" *** ",
          "*   *",
          "  ** ",
          "*   *",
          " *** "],

    '4': ["*   *",
          "*   *",
          "*****",
          "    *",
          "    *"],

    '5': ["*****",
          "*    ",
          "**** ",
          "    *",
          "**** "],

    '6': [" *** ",
          "*    ",
          "**** ",
          "*   *",
          " *** "],

    '7': ["*****",
          "    *",
          "   * ",
          "  *  ",
          " *   "],

    '8': [" *** ",
          "*   *",
          " *** ",
          "*   *",
          " *** "],

    '9': [" *** ",
          "*   *",
          " ****",
          "    *",
          " *** "],

    ' ': ["     ",
          "     ",
          "     ",
          "     ",
          "     "],

    '.': ["   ",
          "   ",
          "   ",
          "   ",
          " * "]
}


def get_birth_date() -> date:
    """
    Запрашивает у пользователя день, месяц и год рождения
    :return:
    """
    print("Введите вашу дату рождения:")

    while True:
        try:
            day = int(input("День: "))
            month = int(input("Месяц: "))
            year = int(input("Год: "))

            return date(year, month, day)
        except ValueError:
            print("Некорректная дата! Попробуйте снова.\n")


def get_weekday(birth_date: date) -> str:
    """
    Определяет день недели для заданной даты
    :param birth_date:
    :return:
    """
    weekday_num = birth_date.weekday()
    return weekdays[weekday_num]


def is_leap_year(year):
    """
    Определяет, является ли год високосным
    :param year:
    :return:
    """
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    return False


def calculate_age(birth_date: date) -> int:
    """
    Вычисляет возраст пользователя
    :param birth_date:
    :return:
    """
    today = date.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def display_date_with_stars(birth_date: date):
    """
    Вывод даты в формате электронного табло
    :param birth_date:
    :return:
    """
    date_string = f"{birth_date.day:02d}.{birth_date.month:02d}.{birth_date.year}"

    symbols = [patterns[c] for c in date_string]

    def get_symbols_for_line(line_number):
        for symbol in symbols:
            for c in symbol[line_number]:
                yield c
            yield ' '

    lines = [
        [c for c in get_symbols_for_line(0)],
        [c for c in get_symbols_for_line(1)],
        [c for c in get_symbols_for_line(2)],
        [c for c in get_symbols_for_line(3)],
        [c for c in get_symbols_for_line(4)]
    ]

    print("=" * 50)
    print("Ваша дата рождения:")
    print("=" * 50)
    for line in lines:
        print("".join(line))
    print("=" * 50)


def main():
    """
    Создайте программу для стилистического преобразования чисел:
    • Напишите программу, которая запрашивает у пользователя последовательно день его рождения, месяц и год;
    • Напишите функцию, которая определяет какому дню недели соответствует эта дата?
    • Напишите функцию, которая определяет - високосный это был год, или нет?
    • Напишите функцию, которая определяет сколько сейчас лет пользователю;
    • Реализуйте вывод в консоль даты рождения пользователя в формате дд мм гггг, где цифры прорисованы звёздочками (*), как на электронном табло.
    :return:
    """
    birth_date = get_birth_date()

    # Проверяем високосный ли год
    if is_leap_year(birth_date.year):
        print(f"Год {birth_date.year} был високосным")
    else:
        print(f"Год {birth_date.year} не был високосным")

    # Вычисляем возраст
    age = calculate_age(birth_date)
    print(f"Ваш возраст: {age} лет. Вы родились в {get_weekday(birth_date)}")

    # Отображаем дату звездочками
    display_date_with_stars(birth_date)


if __name__ == "__main__":
    main()
