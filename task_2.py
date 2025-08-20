class Turtle:

    def __init__(self, x=0, y=0, s=2):
        super().__init__()
        self.x = x
        self.y = y
        self.s = s

    def go_up(self):
        self.y += self.s

    def go_down(self):
        self.y -= self.s

    def go_left(self):
        self.x -= self.s

    def go_right(self):
        self.x += self.s

    def evolve(self):
        self.s += 1

    def degrade(self):
        if (self.s - 1) <= 0:
            raise ValueError("S не может быть <= 0")
        self.s -= 1

    def count_moves(self, x2, y2):
        dx = abs(x2 - self.x)
        dy = abs(y2 - self.y)

        moves_x = dx // self.s
        moves_y = dy // self.s

        remainder_x = dx % self.s
        remainder_y = dy % self.s

        if remainder_x > 0:
            moves_x += 1
        if remainder_y > 0:
            moves_y += 1

        return moves_x + moves_y
