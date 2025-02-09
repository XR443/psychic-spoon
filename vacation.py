import sys
inputNumber = None

if len(sys.argv) > 1:
    inputNumber = int(sys.argv[1])

if inputNumber is None:
    inputNumber = int(input("How many days before your vacation?\n"))

if inputNumber==6:
    print(1)
else:
    print(inputNumber // 7 * 2)