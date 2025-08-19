import collections

pets = dict()


def create():
    elements = collections.deque(pets, maxlen=1)
    if len(elements) > 0:
        last = elements[0]
        new_id = last + 1
    else:
        new_id = 1

    pet_name = input("Введите кличку питомца: ").strip()
    pet_type = input("Введите вид питомца: ").strip()
    pet_age = int(input("Введите возраст питомца: ").strip())
    pet_owner = input("Введите имя владельца: ").strip()
    pet_info = {
        "type": pet_type,
        "age": pet_age,
        "owner": pet_owner,
    }

    update_pets(new_id, pet_name, pet_info)


def read():
    pet_id = int(input("Введите ID питомца: "))
    pet: dict = get_pet(pet_id)
    if not pet:
        print("Питомца с таким ID не существует")
        return

    print_info(pet)


def update():
    pet_id = int(input("Введите ID питомца: "))
    pet: dict = get_pet(pet_id)
    if not pet:
        print("Питомца с таким ID не существует")
        return

    print_info(pet)

    print("Если не желаете изменять поле оставьте его пустым")

    for pet_name, pet_info in pet.items():
        new_name = input(f"Введите новую кличку питомца ({pet_name}): ").strip()
        type = input(f"Введите новый вид питомца ({pet_info["type"]}): ").strip()
        age = int(input(f"Введите новый возраст питомца ({pet_info["age"]}): ").strip())
        owner = input(f"Введите новый имя владельца ({pet_info["owner"]}): ").strip()

        pet_info["type"] = type or pet_info["type"]
        pet_info["age"] = age or pet_info["age"]
        pet_info["owner"] = owner or pet_info["owner"]

    if new_name:
        update_pets(pet_id, new_name, pet_info)

    print_info(pet)


def delete():
    pet_id = int(input("Введите ID питомца: "))
    pet: dict = get_pet(pet_id)
    if not pet:
        print("Питомца с таким ID не существует")
        return

    print_info(pet)

    if input("Вы уверены, что хотите удалить питомца? (y/n): ") == "y":
        del pets[pet_id]
    else:
        print("Удаление отменено")


def update_pets(id, pet_name, pet_info):
    pets[id] = {
        pet_name: pet_info
    }


def get_suffix(age):
    if age % 10 == 1 and age % 100 != 11:
        return "год"
    elif age % 10 in (2, 3, 4) and age % 100 not in (12, 13, 14):
        return "года"
    else:
        return "лет"


def get_pet(id):
    return pets[id] if id in pets else False


def print_info(pet: dict):
    for pet_name, pet_info in pet.items():
        print(
            f'Это {pet_info["type"]} по кличке "{pet_name}". Его возраст {pet_info["age"]} {get_suffix(pet_info["age"])}.',
            f'Имя владельца: {pet_info["owner"]}'
        )


def pets_list():
    if not pets:
        print("База данных питомцев пуста!")
        return

    print("\n=== СПИСОК ВСЕХ ПИТОМЦЕВ ===")
    for pet_id, pet_info in pets.items():
        print_info(pet_info)
    print("=" * 30)


print("Доступные команды: create, read, update, delete, stop")
command = ""
while command != "stop":
    command = input("Введите команду: ").lower().strip()

    if command == "create":
        create()
    elif command == "read":
        read()
    elif command == "update":
        update()
    elif command == "delete":
        delete()
    elif command == "stop":
        break
    else:
        print("Доступные команды: create, read, update, delete, stop")

pets_list()
