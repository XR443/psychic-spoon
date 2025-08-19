n: int = int(input("Введите число: "))

nums = [int(x) for x in input("Введите числа: ").strip().split(' ')]

if len(nums) !=n:
    raise ValueError("Количество введенных чисел не равно первому введенному числу")

shifted_nums = []
for i in range(len(nums) - 1, 2 * len(nums) - 1):
    shifted_nums.append(nums[i % len(nums)])

print(nums)
print(shifted_nums)
