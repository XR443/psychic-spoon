import random


def generate_matrix(n, m):
    rand = random.Random()
    result = []
    for i in range(n):
        result.append([rand.randint(-10, 10) for _ in range(m)])

    return result


def sum_matrix(matrix_l, matrix_r):
    if len(matrix_l) != len(matrix_r) and len(matrix_l[0]) != len(matrix_r[0]):
        raise ValueError("Матрицы должны быть одной размерности")

    n = len(matrix_l)

    result = []
    for i in range(n):
        result.append([x + y for x, y in zip(matrix_l[i], matrix_r[i])])

    return result


matrix_1 = generate_matrix(10, 10)
matrix_2 = generate_matrix(10, 10)

print(sum_matrix(matrix_1, matrix_2))
