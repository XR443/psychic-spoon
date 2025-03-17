"""
создайте класс `Car`, наследник `Vehicle`
"""
from homework_06.base import Vehicle
from homework_06.engine import Engine


class Car(Vehicle):

    def __init__(self, engine: Engine, weight: float = 1000, fuel: float = 0, fuel_consumption: float = 10):
        super().__init__(weight, fuel, fuel_consumption)
        self.engine = engine

    def set_engine(self, engine: Engine):
        self.engine = engine
