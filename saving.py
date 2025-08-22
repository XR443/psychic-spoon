import json
from abc import abstractmethod, ABC


class Savable(ABC):
    @abstractmethod
    def dump(self) -> dict:
        ...


class Loadable(ABC):
    @abstractmethod
    def load(self, saved: dict):
        ...


def save_game(*args):
    result = dict()
    for arg in args:
        if isinstance(arg, Savable):
            result[type(arg).__name__] = arg.dump()
    with open("save.json", 'w') as f:
        json.dump(result, f)
