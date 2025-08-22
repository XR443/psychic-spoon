import json
from pathlib import Path

from board import GameMap
from draw_utils import clear_screen
from entities import Player
from gameplay import run_keyboard_listener, Gameplay

game_map = GameMap(offset=3)
game_map.grow_trees(10)
player = Player()
gameplay = Gameplay(player, game_map)
save_file = Path("save.json")
if save_file.exists():
    with open("save.json", 'r') as f:
        loads = json.load(f)
        player.load(loads)
        gameplay.load(loads)
        game_map.load(loads)

clear_screen()

run_keyboard_listener(gameplay)
gameplay.start()
