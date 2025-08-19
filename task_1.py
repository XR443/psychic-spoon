def recursive_print(vals):
    def index_print(vals, index):
        if 0 <= index < len(vals):
            print(vals[index], end=' ')
            index_print(vals, index - 1)

    index_print(vals, len(vals) - 1)
    print("Конец списка")


my_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
recursive_print(my_list)
