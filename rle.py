import sys

input_str = None

if len(sys.argv) > 1:
    input_str = sys.argv[1]

if not input_str:
    input_str = input("Input a string: ")

result: list = list()

current_char = input_str[0]
counter: int = 0
for char in input_str:
    if current_char == char:
        counter += 1
    else:
        result.append( f"{counter}{current_char}")
        counter = 1
        current_char = char
else:
    result.append(f"{counter}{current_char}")

print("".join(result))
