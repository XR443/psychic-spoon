from argparse import ArgumentError

number_str: str = input("Введите пятизначное число: ")
if len(number_str) != 5:
    raise ArgumentError

number: int = int(number_str)

first = number % 10
second = number // 10 % 10
third = number // 100 % 10
fourth = number // 1000 % 10
fifth = number // 10000 % 10

result = (second**first) * third / (fifth - fourth)

print(result)
