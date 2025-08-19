import re

original_string: str = input("Введите слово: ")

print(re.sub(r' +', ' ', original_string))
