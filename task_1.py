n: int = int(input("Введите число: "))

nums = {int(x) for x in input("Введите числа: ").strip().split(' ')}

print(len(nums))