def find_places(rows: list, number_of_places: int):
    for i, row in enumerate(rows):
        places_in_row = __find_places_in_row(row, number_of_places)
        if places_in_row:
            return i
    else:
        return False


def __find_places_in_row(row: list, number_of_places: int):
    counter: int = 0

    for place in row:
        if not place:
            counter += 1
        else:
            if counter >= number_of_places:
                return True
            counter = 0
    else:
        return counter >= number_of_places


print(find_places([[0, 1, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], 2))
print(find_places([[0, 1, 1, 0], [1, 0, 1, 0], [1, 1, 0, 1]], 2))
