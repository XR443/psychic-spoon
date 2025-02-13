card: dict = {}

while True:
    input_str: str = input("Введите строку таблицы, разделяя столбцы через пробел:\n"
                           "Название предмета | Фамилия | Оценка\n")
    if not input_str.strip():
        break

    course, student, score = input_str.split(' ')

    if not course in card:
        card.update({course: {student: [score]}})
    elif not student in card[course]:
        card[course].update({student: [score]})
    else:
        card[course][student] += score

for course in card:
    print(course)
    for student in card[course]:
        print(f"{student}: {', '.join(card[course][student])}\n")

