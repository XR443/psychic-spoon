import traceback
from threading import Thread
from time import sleep

from pynput import keyboard
from pynput.keyboard import Key

from board import GameMap, CLOUD, STORM
from draw_utils import clear_screen, print_at
from entities import Player
from saving import Savable, save_game, Loadable


class Gameplay(Savable, Loadable):

    def __init__(self, player: Player, game_map: GameMap, tick_delay=0.01, combustion_time=1000, score_per_fire=100,
                 trees_in_fire=None
                 ):
        self.__score_per_fire = score_per_fire
        self._player = player
        self._map = game_map
        self.__tick_delay = tick_delay
        self.__ticks = 0
        self.__trees_in_fire = trees_in_fire or list()
        game_map.set_player(player)

        self.__combustion_time = combustion_time

        self._previous_weather = None
        self._previous_weather_tick = 0

        self.game_running = False

    def start(self):
        self.game_running = True
        Thread(target=self._tick, args=(self._map, self._player, self.__tick_delay)).start()

    def _tick(self, game_map: GameMap, player: Player, tick_delay):
        try:
            while self.game_running and player.health > 0 and game_map.has_trees():
                self.__ticks += 1

                self.check_weather(self.__ticks)
                if player.health <= 0:
                    continue

                self.check_fire(self.__ticks)

                if not self.__ticks % 1000:
                    self.add_fire(self.__ticks)
                if not self.__ticks % 1500:
                    game_map.change_weather()
                if not self.__ticks % 10000:
                    game_map.grow_trees(3)

                clear_screen()
                game_map.print_map(self.__ticks)
                sleep(tick_delay)
            else:
                clear_screen()
                if player.health <= 0:
                    end_message = "Пилоту стало плохо :("
                elif not game_map.has_trees():
                    end_message = "Все деревья сгорели :("
                else:
                    save_game(self, player, game_map)
                    end_message = "Вы завершили игру."
                print_at(1, 1, "Игра окончена! " + end_message)
                print_at(2, 1, f"Ваш счёт: {player.score}")
        except Exception as e:
            print(e)
            traceback.print_exc()

    def process_key(self, key):
        try:
            self.__process_move(key)
            self.__process_action(key)
        except Exception as e:
            self.game_running = False
            print(e)

    def __process_move(self, key):
        dx = 0
        dy = 0
        if key == Key.up:
            dy = -1
        elif key == Key.down:
            dy = 1
        elif key == Key.left:
            dx = -1
        elif key == Key.right:
            dx = 1
        self._map.update_player_position(dx, dy)

        self.check_weather(None)

    def __process_action(self, key):
        if key == Key.space:
            if self._map.is_player_over_water():
                self._player.fill()
            elif self._map.is_player_over_interactable_entity():
                entity = self._map.get_interactable_entity_under_player()
                if entity:
                    entity.interact(self._player)
            else:
                if self._player.has_water():
                    if self._map.extinguish():
                        self._player.score += self.__score_per_fire
                self._player.empty()
        if key == Key.esc:
            self.game_running = False

    def add_fire(self, ticks, tree=None):
        if tree:
            coordinates = [
                (tree[0] - 1, tree[1] - 1), (tree[0], tree[1] - 1), (tree[0] + 1, tree[1] - 1),
                (tree[0] - 1, tree[1]), (tree[0] + 1, tree[1]),
                (tree[0] - 1, tree[1] + 1), (tree[0], tree[1] + 1), (tree[0] + 1, tree[1] + 1),
            ]
            self.__trees_in_fire.append({ticks: self._map.fire_trees(coordinates=coordinates)})
        else:
            self.__trees_in_fire.append({ticks: self._map.fire_trees()})

    def check_fire(self, ticks):
        trees_to_check = self.__trees_in_fire.copy()
        for i, trees_with_tick in enumerate(trees_to_check):
            for tick, trees in trees_with_tick.items():
                if tick + self.__combustion_time <= ticks:
                    trees_burned = self._map.burned_down(trees)
                    self._player.score -= self.__score_per_fire * len(trees_burned)
                    for tree in trees_burned:
                        self.add_fire(ticks, tree)
                    self.__trees_in_fire.pop(0)

    def check_weather(self, ticks):
        weather = self._map.get_player_weather()

        # Если погоды нет, значит нет
        if not weather:
            self._previous_weather = None
            self._previous_weather_tick = None
            return

            # Если нет тиков, значит только зашли в клетку
        if not ticks:
            self._previous_weather = weather
            self._previous_weather_tick = None
            weather.interact(self._player)
            return

        # Если раньше тиков не было значит текущий первый тик нахождения в этой погоде
        if not self._previous_weather_tick:
            self._previous_weather_tick = ticks

        if (self._previous_weather is None
                or weather == self._previous_weather and abs(self._previous_weather_tick - ticks) >= 100):
            weather.interact(self._player)
            self._previous_weather = weather
            self._previous_weather_tick = ticks

    def dump(self) -> dict:
        return {
            "score_per_fire": self.__score_per_fire,
            "trees_in_fire": self.__trees_in_fire,
            "combustion_time": self.__combustion_time,
            "previous_weather": self._previous_weather,
            "previous_weather_tick": self._previous_weather_tick,
            "ticks": self.__ticks,
        }

    def load(self, saved: dict):
        values = saved[type(self).__name__]
        self.__score_per_fire = values["score_per_fire"]
        self.__trees_in_fire = [{int(key): [(c[0], c[1]) for c in value]}
                                for trees_map in values["trees_in_fire"]
                                for key, value in trees_map.items()]
        self.__trees_in_fire.sort(key=lambda x: [y for y in x.keys()][0])
        self.__combustion_time = values["combustion_time"]
        self._previous_weather = self.__map_weather(values["previous_weather"])
        self._previous_weather_tick = values["previous_weather_tick"]
        self.__ticks = values["ticks"]

    @staticmethod
    def __map_weather(previous_weather):
        entities = {type(e).__name__: e for e in [CLOUD, STORM]}
        if previous_weather in entities:
            return entities[previous_weather]
        return None

    @staticmethod
    def __text_list_as_list_tuple(text_list):
        result = []
        for s in text_list:
            left, right = s.split(':')
            result.append((int(left), int(right)))
        return result


def run_keyboard_listener(gameplay: Gameplay):
    def process_key(key):
        gameplay.process_key(key)

    listener = keyboard.Listener(on_release=process_key)
    listener.start()
