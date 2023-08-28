from config import Character
from player import Player

class GameState:
    def __init__(self, character: Character, ascention: int):
        self.player = Player(character)
        self.ascention = ascention