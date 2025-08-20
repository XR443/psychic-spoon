class CashRegister:

    def __init__(self):
        super().__init__()
        self.money = 0

    def top_up(self, x):
        self.money += x

    def take_away(self, x):
        if self.money < x:
            raise ValueError("Недостаточно средств")
        self.money -= x

    def count_1000(self):
        return self.money // 1000


register = CashRegister()

register.top_up(999)
print(register.count_1000())

register.top_up(2)
print(register.count_1000())

register.take_away(1001)
print(register.count_1000())
try:
    register.take_away(1)
except ValueError as e:
    print(e)
