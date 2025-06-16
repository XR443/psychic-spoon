vowels = {'a': 0, 'e': 0, 'i': 0, 'o': 0, 'u': 0}
consonants = 0

for char in input("Введите слово: "):
    if char in vowels:
        vowels[char] += 1
    else:
        consonants += 1

print(not any([not val for key, val in vowels.items()]))

