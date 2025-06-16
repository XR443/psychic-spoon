number: int = int(input("Введите число: "))

positivity = ""
parity = ""

if number % 2:
    parity = "нечетное"
else:
    parity = "четное"

if number == 0:
    positivity = ""
    parity = "нулевое"
elif number<0:
    positivity = "отрицательное"
else:
    positivity = "положительное"

print(f"{positivity} {parity} число".strip())
