n: int = int(input("Введите число: "))

if n<=0:
    raise ValueError("Число должно быть натуральным")

count = 1
for x in range(1, n):
    if not n % x:
        count += 1

print(f"Существует {count} делителей числа {n}".strip())
