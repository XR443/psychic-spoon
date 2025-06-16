startup_needs: float = float(input("Введите сколько денег необходимо стартапу: "))
michael_money: float = float(input("Введите количество денег Майкла: "))
ivan_money: float = float(input("Введите количество денег Ивана: "))

if ivan_money >= startup_needs and michael_money >= startup_needs:
    print(2)
elif ivan_money >= startup_needs > michael_money:
    print("Ivan")
elif michael_money >= startup_needs > ivan_money:
    print("Mike")
elif ivan_money + michael_money >= startup_needs:
    print(1)
elif ivan_money + michael_money < startup_needs:
    print(0)

