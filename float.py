import sys
import re

inputNumber: str = None

if len(sys.argv) > 1:
    inputNumber = sys.argv[1]

if inputNumber is None:
    inputNumber = input("Input a number: ")

numbers_regex = re.compile(r'''
                            [0-9]
                            ''', re.VERBOSE)

dot_regex = re.compile(r'''
                            \.
                            ''', re.VERBOSE)

minus_sign_regex = re.compile(r'''
                            -
                            ''', re.VERBOSE)

is_positive: bool = True
is_dot_found: bool = False
is_first_char: bool = True

result: bool = True

for i in range(0, len(inputNumber)):
    char = inputNumber[i]

    if is_first_char:
        is_first_char = False
        if minus_sign_regex.match(char):
            is_positive = False
            continue

    if dot_regex.match(char):
        if is_dot_found:
            result = False
            break
        is_dot_found = True
    elif not numbers_regex.match(char):
        result = False
        break

print(f"Is float number: {result}")
print(f"Is positive number: {is_positive}")
