original_string: str = input("Введите слово: ")

reversed_string = original_string[::-1]

if original_string == reversed_string:
    print("yes")
else:
    print("no")
