import sys

input_number = None

if len(sys.argv) > 1:
    input_number = int(sys.argv[1])

if input_number is None:
    input_number = int(input("Input a number: "))

number: int = input_number

digits_sum: int = 0

while not 0 <= number <= 9:
    rest_number = number
    while rest_number != 0:
        last_digit = rest_number % 10
        rest_number = rest_number // 10
        digits_sum += last_digit
    number = digits_sum
    digits_sum = 0

print(number)
