boat_payload_kg: int = int(input("Введите грузоподъемность лодки: "))
fisherman_count: int = int(input("Введите количество рыбаков: "))
boat_payload_mans: int = 2

weights = []

for _ in range(fisherman_count):
    weight: int = int(input("Введите вес рыбака: "))
    weights.append(weight)

sorted_weights = sorted(weights)

boats = 0
i = 0
while i < len(weights) - 1:
    if sorted_weights[i] + sorted_weights[i + 1] <= boat_payload_kg:
        boats += 1
        i += 2
    else:
        boats += len(weights) - i
        break

print(f"Необходимо {boats} лодок")
