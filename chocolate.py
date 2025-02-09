width: int = int(input("Input chocolate width: "))
length: int = int(input("Input chocolate length: "))
wantedSize: int = int(input("Input wanted chocolate size: "))

result: bool = False

for i in range(1, width + 1):
    if (i * length) == wantedSize:
        result = True
        break

if not result:
    for i in range(1, length + 1):
        if (i * width) == wantedSize:
            result = True
            break

print(result)
