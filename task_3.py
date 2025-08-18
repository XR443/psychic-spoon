a: int = int(input("Введите число A: "))
b: int = int(input("Введите число B: "))

print(' '.join([str(x) for x in range(a, b + 1) if not x % 2]))
