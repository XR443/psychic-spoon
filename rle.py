import sys

input_str = None

if len(sys.argv) > 1:
    input_str = sys.argv[1]

if input_str is None:
    input_str = input("Input a string: ")

result: str = ''

current_char = None
counter: int = 0
for char in input_str:
    if not current_char:
        current_char = char
        counter = 1
    else:
        if current_char == char:
            counter += 1
        else:
            result += f"{counter}{current_char}"
            counter = 1
            current_char = char
else:
    result += f"{counter}{current_char}"

print(result)
