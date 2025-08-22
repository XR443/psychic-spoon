from abc import abstractmethod, ABC

from saving import Savable, Loadable


class Entity(Savable, ABC):

    def __init__(self, icon: str):
        self.icon = icon

    @abstractmethod
    def info(self) -> str:
        pass

    def __str__(self):
        return self.icon

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value

    def dump(self) -> dict:
        return {
            "value": self.icon,
        }


class Player(Entity, Loadable):

    def __init__(self, max_health=3, water_tank_max=1):
        super().__init__('🚁')
        self.water_tank_max = water_tank_max
        self.water_tank = 0
        self.health_max = max_health
        self.health = max_health
        self.score = 0

    def upgrade_water_tank(self, value=1):
        """
        Увеличиваем максимальное количество воды на параметр
        :param value: сколько добавить к максимальному значению воды
        :return:
        """
        self.water_tank_max += value

    def downgrade_water_tank(self, value=1):
        """
        Уменьшает максимальное количество воды на параметр
        :param value: сколько отнять от максимального значению воды
        :return: Успешно ли изменение значения контейнера. True если итоговое значение > 0, False если итоговое значение <= 0.
        """
        if self.water_tank_max - value > 0:
            self.water_tank_max -= value
            return True
        return False

    def fill(self, value=None):
        """
        Наливает воду в бак
        :param value: сколько налить воды, если None - набирает весь бак
        :return:
        """
        if value:
            self.water_tank = min(self.water_tank + value, self.water_tank_max)
        else:
            self.water_tank = self.water_tank_max

    def empty(self, value=1):
        """
        Выливает воду из бака
        :param value: сколько вылить воды
        :return:
        """
        self.water_tank = max(self.water_tank - value, 0)

    def heal(self, value=1):
        self.health = min(self.health + value, self.health_max)

    def has_water(self):
        return self.water_tank > 0

    def info(self) -> str:
        return "Летчик-вертолетчик"

    def damaged(self):
        return self.health < self.health_max

    def dump(self) -> dict:
        return {
            "water_tank_max": self.water_tank_max,
            "water_tank": self.water_tank,
            "health_max": self.health_max,
            "health": self.health,
            "score": self.score,
        }

    def load(self, saved: dict):
        values = saved[type(self).__name__]
        self.water_tank_max = values["water_tank_max"]
        self.water_tank = values["water_tank"]
        self.health_max = values["health_max"]
        self.health = values["health"]
        self.score = values["score"]


class Tree(Entity):

    def __init__(self):
        super().__init__('🌳')

    def info(self) -> str:
        return "Это дерево. Надо следить чтоб не загорелось."


class Water(Entity):

    def __init__(self):
        super().__init__('💦')

    def info(self) -> str:
        return "Это вода. Может помочь при тушении пожара."


class Fire(Entity):

    def __init__(self):
        super().__init__('🔥')

    def info(self) -> str:
        return "ПОЖАР!!!"


class Grass(Entity):

    def __init__(self):
        super().__init__('🌿')

    def info(self) -> str:
        return "Травушка-муравушка"


class Interactable(ABC):
    @abstractmethod
    def interact(self, player: Player):
        ...


class Cloud(Entity, Interactable):

    def __init__(self, icon='☁️'):
        super().__init__(icon)

    def info(self) -> str:
        return "Облачко воздушное. Ничего не видно"

    def interact(self, player: Player):
        pass


class Storm(Cloud):

    def __init__(self):
        super().__init__('🌧️')

    def info(self) -> str:
        return "Гроза. БЕРЕГИСЬ!!!"

    def interact(self, player: Player):
        player.health -= 1


class Store(Entity, Interactable, Loadable):

    def __init__(self, price=500, price_increase=0.5):
        super().__init__('🛠️')
        self._price = price
        self.__price_increase = price_increase

    def interact(self, player: Player):
        if player.score >= self._price:
            player.upgrade_water_tank()
            player.score -= self._price
            self._price += int(self._price * self.__price_increase)

    def info(self) -> str:
        return f"Магазин улучшений. Стоимость улучшения: {self._price}"

    def dump(self) -> dict:
        return {
            "price": self._price,
            "price_increase": self.__price_increase,
        }

    def load(self, saved: dict):
        values = saved[type(self).__name__]
        self._price = values["price"]
        self.__price_increase = values["price_increase"]


class Hospital(Entity, Interactable, Loadable):

    def __init__(self, price=1000, price_increase=0.25):
        super().__init__('🏥')
        self._price = price
        self.__price_increase = price_increase

    def interact(self, player: Player):
        if player.score >= self._price and player.damaged():
            player.heal()
            player.score -= self._price
            self._price += int(self._price * self.__price_increase)

    def info(self) -> str:
        return f"Больница. Стоимость лечения: {self._price}"

    def dump(self) -> dict:
        return {
            "price": self._price,
            "price_increase": self.__price_increase,
        }

    def load(self, saved: dict):
        values = saved[type(self).__name__]
        self._price = values["price"]
        self.__price_increase = values["price_increase"]
