from abc import ABC

from homework_06.exceptions import LowFuelError, NotEnoughFuel


class Vehicle(ABC):

    def __init__(self, weight: float = 1000, fuel: float = 0, fuel_consumption: float = 10):
        super().__init__()
        self.weight = weight
        self.fuel = fuel
        self.fuel_consumption = fuel_consumption
        self.started = False

    def start(self):
        if not self.started:
            if self.fuel > 0:
                self.started = True
            else:
                raise LowFuelError

    def move(self, distance: float):
        requires_fuel = distance * self.fuel_consumption
        if requires_fuel > self.fuel:
            raise NotEnoughFuel
        self.fuel = -requires_fuel
