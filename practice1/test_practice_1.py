import datetime
from datetime import date

import pytest

from practice_1 import get_weekday, is_leap_year, calculate_age


@pytest.mark.parametrize("test_date, expected_weekday", [
    (date(2026, 9, 7), "Понедельник"),
    (date(2026, 9, 8), "Вторник"),
    (date(2026, 9, 9), "Среда"),
    (date(2026, 9, 10), "Четверг"),
    (date(2026, 9, 11), "Пятница"),
    (date(2026, 9, 12), "Суббота"),
    (date(2026, 9, 13), "Воскресенье"),
])
def test_get_week_day(test_date, expected_weekday):
    assert get_weekday(test_date) == expected_weekday


@pytest.mark.parametrize("year, expected", [
    (2020, True),
    (2000, True),
    (2026, False),
    (1900, False),
])
def test_is_leap_year(year, expected):
    assert is_leap_year(year) == expected


def get_changed_date(test_date: date, years=0, months=0, days=0) -> date:
    return test_date.replace(year=test_date.year + years, month=test_date.month + months, day=test_date.day + days)


@pytest.mark.parametrize("test_date, expected", [
    (get_changed_date(date.today(), years=-7), 7),
    (get_changed_date(date.today(), years=-7, days=-1), 7),
    (get_changed_date(date.today(), years=-7, months=-1), 7),
    (get_changed_date(date.today(), years=-7, months=-1, days=-1), 7),
    (get_changed_date(date.today(), years=-7, days=1), 6),
    (get_changed_date(date.today(), years=-7, months=1), 6),
    (get_changed_date(date.today(), years=-7, months=1, days=1), 6),
])
def test_calculate_age(test_date, expected):
    assert calculate_age(test_date) == expected
