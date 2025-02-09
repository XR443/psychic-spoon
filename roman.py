import sys

inputNumber = None

if len(sys.argv) > 1:
    inputNumber = int(sys.argv[1])

if inputNumber is None:
    inputNumber = int(input("Input a number: "))

roman = {
    1: 'I',
    5: 'V',
    10: 'X',
    50: 'L',
    100: 'C',
    500: 'D',
    1000: 'M',
}

modifier: int = 1000

result: str = ""

while modifier > 0:
    digit = inputNumber // modifier

    if 1 <= digit < 4: # если цифра от 1 до 4, то нам не нужно никаких доп ухищрений
        result += roman[1 * modifier] * digit
    elif digit == 4: # при цифре 4 необходимо:
        if (5 * modifier) in roman: # проверить существует ли 5 в текущем модификаторе и если да, то записать
            result += roman[1 * modifier]
            result += roman[5 * modifier]
        else: # если нет, то пишем как число 1 несколько раз
            result += roman[1 * modifier] * digit
    elif digit == 5: # при цифре 5 необходимо:
        if (5 * modifier) in roman:  # проверить существует ли 5 в текущем модификаторе и если да, то записать
            result += roman[5 * modifier]
        else: # если нет, то пишем как число 1 несколько раз
            result += roman[1 * modifier] * digit
    elif 5 < digit < 9: # если цифра от 6 до 8, то нам не нужно никаких доп ухищрений
        result += roman[5 * modifier]
        result += roman[1 * modifier] * (digit - 5)
    elif digit >= 9: # при цифре 9 и более (для тысяч) необходимо:
        if (1 * modifier * 10) in roman: # проверить существует ли 1 в следующем модификаторе и если да, то записать
            result += roman[1 * modifier]
            result += roman[1 * modifier * 10]
        else: # если нет, то пишем как число 1 несколько раз
            result += roman[1 * modifier] * digit

    inputNumber %= modifier
    modifier //= 10

print(result)
