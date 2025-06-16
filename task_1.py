animal_type: str = input("Введите вид животного: ")
animal_name: str = input("Введите кличку животного: ")
animal_age: int = int(input("Введите возраст животного: "))

def year_str(age: int):
    if age % 100 in (11, 12, 13, 14):
        return 'лет'
    last_digit = age % 10
    if last_digit == 1:
        return 'год'
    elif last_digit in (2, 3, 4):
        return 'года'
    else:
        return 'лет'

print(f'Это {animal_type} по кличке "{animal_name}". Его возраст {animal_age} {year_str(animal_age)}')