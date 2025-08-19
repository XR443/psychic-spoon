pets = dict()
while True:
    answer = input("Вы хотите ввести животное? (y/n) >")
    if answer == 'n':
        break
    elif answer == 'y':
        pets[input("Введите кличку питомца: ").strip()] = {
            "type": input("Введите вид питомца: ").strip(),
            "age": int(input("Введите возраст питомца: ").strip()),
            "owner": input("Введите имя владельца: ").strip(),
        }


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


for pet_name, pet_info in pets.items():
    print(f'Это {pet_info["type"]} по кличке "{pet_name}". Его возраст {pet_info["age"]} {year_str(pet_info["age"])}.',
          f'Имя владельца: {pet_info["owner"]}')
