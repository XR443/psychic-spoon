def factorial(n):
    if n < 0:
        raise ValueError("Факториал определен только для неотрицательных чисел")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

start_num = int(input("Введите число: "))

print([factorial(num) for num in range(factorial(start_num), 0, -1)])