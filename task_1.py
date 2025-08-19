n: int = int(input("Введите число: "))

nums = []

for _ in range(n):
    num: int = int(input("Введите число: "))
    nums.append(num)

print([x for x in reversed(nums)])