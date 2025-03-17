"""
create dataclass `Engine`
"""
from dataclasses import dataclass

@dataclass
class Engine:
    def __init__(self, volume: float = 3, pistons: int = 6):
        super().__init__()
        self.volume = volume
        self.pistons = pistons
