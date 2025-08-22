def clear_screen():
    """Очищает консоль"""
    print("\033[H\033[J", end="")


def print_at(row, col, text):
    """Выводит текст в указанной позиции консоли"""
    print(f"\033[{row};{col}H{text}", end="")
