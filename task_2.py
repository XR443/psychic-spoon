nums_1 = {int(x) for x in input("Введите числа: ").strip().split(' ')}
nums_2 = {int(x) for x in input("Введите числа: ").strip().split(' ')}

print(len(nums_1 & nums_2))
