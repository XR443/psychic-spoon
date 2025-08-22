import random
import sys
from typing import Tuple, Dict, override

from draw_utils import print_at
from entities import Player, Water, Tree, Fire, Grass, Interactable, Entity, Store, Cloud, Storm, Hospital
from saving import Savable, Loadable

GRASS = Grass()
WATER = Water()
TREE = Tree()
FIRE = Fire()

CLOUD = Cloud()
STORM = Storm()


class GameMap(Savable, Loadable):

    def __init__(self, width=20, height=10, water_percent=0.2, offset=3, random_state=None,
                 coordinate_map=None,
                 cloud_map=None,
                 player_position=None,
                 trees=None,
                 fires=None,
                 ):
        self.random = random.Random(random_state)
        self.width = width
        self.height = height
        self._offset = offset + 1
        self._player: Player = None

        self._coordinate_map: Dict[Tuple[int, int], Entity] = coordinate_map or dict()
        self._cloud_map: Dict[Tuple[int, int], Entity] = cloud_map or dict()

        if not coordinate_map:
            self.__fill_coordinate_with_entity(self._get_coordinates(percent=water_percent), WATER)
            self.__fill_coordinate_with_entity(self._get_coordinates(count=2), Store, new=True)
            self.__fill_coordinate_with_entity(self._get_coordinates(count=1), Hospital, new=True)

        self._player_position = player_position or (self.width // 2, self.height // 2)
        self._trees = trees or set()
        self._fires = fires or set()

    def _get_coordinates(self, percent=None, count=None):
        """
        Вспомогательный метод получения случайных координат внутри карты
        :param percent: процент от площади (максимально)
        :param count: количество координат (максимально)
        :return:
        """
        if (percent and count) or (not percent and not count):
            raise ValueError("Должно быть заполнено либо количество, либо процент поля")
        if percent:
            return {(self.random.randint(0, self.width), self.random.randint(0, self.height))
                    for _ in range(int(self.width * self.height * percent))}
        if count:
            return {(self.random.randint(0, self.width), self.random.randint(0, self.height))
                    for _ in range(count)}

    def __fill_coordinate_with_entity(self, coordinates, entity, new=False):
        for coordinate in coordinates:
            if not coordinate in self._coordinate_map:
                if new:
                    self._coordinate_map[coordinate] = entity()
                else:
                    self._coordinate_map[coordinate] = entity

    def print_map(self, ticks=None):
        """
        Метод для печати в консоль карты
        :return:
        """
        print_at(0, 0, "Управление вертолетом: ←, →, ↑, ↓. Действие: Пробел.")
        print_at(self._offset - 1, 0,
                 f"Резервуар {self._player.water_tank}/{self._player.water_tank_max}\t HP: {self._player.health}/{self._player.health_max}")
        for i in range(self.height):
            row = []
            for j in range(self.width):
                to_append = GRASS
                if (j, i) == self._player_position:
                    to_append = self._player
                elif (j, i) in self._coordinate_map:
                    to_append = self._coordinate_map[(j, i)]

                if (j, i) in self._cloud_map:
                    to_append = self._cloud_map[(j, i)]

                row.append(to_append.icon)

            print_at(i + self._offset, 0, ' '.join(row))

        print_at(self.height + self._offset + 1, 1, self.__get_info_about_coordinate(self._player_position))

        if ticks:
            print_at(self.height + self._offset + 2, 1, f"Счёт: {self._player.score}\tТекущие тики: {ticks}")
        else:
            print_at(self.height + self._offset + 2, 1, f"Счёт: {self._player.score}")

        sys.stdout.flush()

    def grow_trees(self, n):
        """
        Метод выращивающий новые деревья
        :param n: сколько деревьев вырастить (максимально)
        :return: список координат новых деревьев
        """
        new_trees = []
        for coordinate in self._get_coordinates(count=n):
            if not coordinate in self._coordinate_map:
                self._coordinate_map[coordinate] = TREE
                self._trees.add(coordinate)
                new_trees.append(coordinate)
        return new_trees

    def has_trees(self) -> bool:
        return len(self._trees) != 0

    def fire_trees(self, n=3, coordinates=None):
        """
        Метод поджигающий деревья
        :param n: сколько деревьев поджечь (максимально)
        :param coordinates: список координат, в котором надо проверить и поджечь деревья
        :return: список координат с пожаром
        """
        trees_to_burn = set()
        number_of_trees = min(n, len(self._trees))

        if coordinates:
            for _ in range(number_of_trees):
                trees_to_burn.add(self.random.choice(coordinates))
        else:
            while len(trees_to_burn) < number_of_trees:
                trees_to_burn.add(self.random.choice(list(self._trees)))

        new_fires = []
        for coordinate in trees_to_burn:
            if coordinate in self._coordinate_map and isinstance(self._coordinate_map[coordinate], Tree):
                self._coordinate_map[coordinate] = FIRE
                self._fires.add(coordinate)
                new_fires.append(coordinate)
        return new_fires

    def burned_down(self, trees) -> list:
        """
        Метод для удаления сожженных деревьев
        :param trees: координаты деревьев, которые были сожжены огнем
        :return: координаты сгоревших деревьев
        """
        trees_burned = []
        for coordinate in trees:
            if coordinate in self._fires:
                trees_burned.append(coordinate)
                del self._coordinate_map[coordinate]
                self._trees.remove(coordinate)
                self._fires.remove(coordinate)
        return trees_burned

    def extinguish(self) -> bool:
        """
        Метод для удаления огня на позиции игрока
        :return: True если потушили огонь, False иначе
        """
        if self._player_position in self._fires:
            self._coordinate_map[self._player_position] = TREE
            self._fires.remove(self._player_position)
            return True
        return False

    def change_weather(self, clouds=10, storm=3):
        self._cloud_map.clear()

        cloud_coordinates = self._get_coordinates(count=clouds)
        storm_coordinates = self._get_coordinates(count=storm)

        for coordinate in cloud_coordinates:
            self._cloud_map[coordinate] = CLOUD
        for coordinate in storm_coordinates:
            self._cloud_map[coordinate] = STORM

    def update_player_position(self, dx, dy):
        """
        Обновляет позицию игрока на карте
        :param dx: изменение по X
        :param dy: изменение по Y
        :return:
        """
        new_position = (self._player_position[0] + dx, self._player_position[1] + dy)
        if 0 <= new_position[0] < self.width and 0 <= new_position[1] < self.height:
            self._player_position = new_position

    def is_player_over_water(self):
        return (self._player_position in self._coordinate_map and
                isinstance(self._coordinate_map[self._player_position], Water))

    def is_player_over_fire(self):
        return (self._player_position in self._fires and
                isinstance(self._coordinate_map[self._player_position], Fire))

    def is_player_over_interactable_entity(self):
        return (self._player_position in self._coordinate_map and
                isinstance(self._coordinate_map[self._player_position], Interactable))

    def get_interactable_entity_under_player(self):
        if (self._player_position in self._coordinate_map and
                isinstance(self._coordinate_map[self._player_position], Interactable)):
            return self._coordinate_map[self._player_position]
        return None

    def get_player_weather(self):
        if (self._player_position in self._cloud_map and
                isinstance(self._cloud_map[self._player_position], Cloud)):
            return self._cloud_map[self._player_position]
        return None

    def set_player(self, player):
        self._player = player

    def __get_info_about_coordinate(self, coordinate):
        obj = GRASS
        if coordinate in self._coordinate_map:
            obj = self._coordinate_map[self._player_position]
        if coordinate in self._cloud_map:
            obj = self._cloud_map[self._player_position]
        return self.__pretty_string(obj.info(), obj)

    @staticmethod
    def __pretty_string(string, obj):
        return f"{obj} {string} {obj}"

    @override
    def dump(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "coordinate_map": self.__map_as_text(self._coordinate_map),
            "cloud_map": self.__map_as_text(self._cloud_map),
            "player_position": self._player_position,
            "trees": self.__list_as_text(self._trees),
            "fires": self.__list_as_text(self._fires),
        }

    def __map_as_text(self, coordinates_map):
        return [{f"{coordinate[0]}:{coordinate[1]}": self.__dump_entity(entity)}
                for coordinate, entity in coordinates_map.items()]

    @staticmethod
    def __dump_entity(entity):
        if isinstance(entity, Savable):
            return {type(entity).__name__: entity.dump()}
        return type(entity).__name__

    @staticmethod
    def __list_as_text(coordinates):
        return [f"{coordinate[0]}:{coordinate[1]}" for coordinate in coordinates]

    def load(self, saved: dict):
        values = saved[type(self).__name__]
        self.width = values["width"]
        self.height = values["height"]
        self._coordinate_map = self.__map_coordinates(values["coordinate_map"])
        self._cloud_map = self.__map_coordinates(values["cloud_map"])
        self._player_position = tuple(values["player_position"])
        self._trees = self.__text_list_as_set_tuple(values["trees"])
        self._fires = self.__text_list_as_set_tuple(values["fires"])

    @staticmethod
    def __text_list_as_set_tuple(text_list):
        result = set()
        for s in text_list:
            left, right = s.split(':')
            result.add((int(left), int(right)))
        return result

    @staticmethod
    def __map_coordinates(game_dict_list):
        entities = {type(e).__name__: e for e in [GRASS, WATER, TREE, FIRE, CLOUD, STORM]}
        loadable_entities = {e.__name__: e for e in [Hospital, Store]}
        result = dict()
        for record in game_dict_list:
            for coordinate_str, entity in record.items():
                left, right = coordinate_str.split(':')
                coordinate = (int(left), int(right))
                for name, value in entity.items():
                    if name in entities:
                        result[coordinate] = entities[name]
                    elif name in loadable_entities:
                        loadable_entity = loadable_entities[name]()
                        loadable_entity.load(entity)
                        result[coordinate] = loadable_entity
                    else:
                        raise ValueError(f"Неизвестный тип сущности {name}")

        return result
