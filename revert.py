import sys

inputNumber = None

if len(sys.argv) > 1:
    inputNumber = int(sys.argv[1])

if inputNumber is None:
    inputNumber = int(input("Input a number with length 5: "))

number: int = inputNumber
lN = number // 1000 % 10
number -= lN * 1000

rN = number // 10 % 10
number -= rN * 10

number += rN * 1000 + lN * 10

print(number)
