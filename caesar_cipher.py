import sys

offset = None
input_str = None

if len(sys.argv) > 2:
    offset = int(sys.argv[1])
    input_str = sys.argv[2]
elif len(sys.argv) > 1:
    input_str = sys.argv[1]

if offset is None:
    offset = int(input("Input cipher offset: "))

if input_str is None:
    input_str = input("Input a string: ")

result: str = ''

lowercase_start: int = ord('a')
lowercase_end: int = lowercase_start + 26

uppercase_start: int = ord('A')
uppercase_end: int = uppercase_start + 26

for char in input_str:
    new_char = char

    if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
        new_char_index = ord(char) + offset
        if (lowercase_start <= new_char_index <= lowercase_end) or (uppercase_start <= new_char_index <= uppercase_end):
            new_char = chr(new_char_index)
        elif uppercase_end < new_char_index < lowercase_start:
            new_char = chr(uppercase_start + (new_char_index - uppercase_end))
        else:  # new_char_index > uppercase_end:
            new_char = chr(lowercase_start + (new_char_index - lowercase_end))

    result += new_char

print(result)
