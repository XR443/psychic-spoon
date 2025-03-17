"""
создайте класс `Plane`, наследник `Vehicle`
"""
from homework_06.base import Vehicle
from homework_06.exceptions import CargoOverload


class Plane(Vehicle):

    def __init__(self, cargo: float = 0,
                 max_cargo: float = 500,
                 weight: float = 1000,
                 fuel: float = 0,
                 fuel_consumption: float = 10):
        super().__init__(weight, fuel, fuel_consumption)
        self.cargo = cargo
        self.max_cargo = max_cargo

    def load(self, cargo: float):
        if self.cargo + cargo > self.max_cargo:
            raise CargoOverload
        self.cargo += cargo

    def remove_all_cargo(self) -> float:
        self.cargo, tmp_cargo = 0, self.cargo
        return tmp_cargo
