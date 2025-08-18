n: int = int(input("Введите число: "))

count = 0
for _ in range(n):
    if not int(input("Введите число: ")):
        count += 1

print(f"{count} чисел не равно нулю".strip())
