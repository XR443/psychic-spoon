nums = [int(x) for x in input("Введите числа: ").strip().split(' ')]

seen_before = set()
for num in nums:
    if num in seen_before:
        print("YES")
    else:
        print("NO")
        seen_before.add(num)
