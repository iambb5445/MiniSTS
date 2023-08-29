from value import Value
from target import CreatureTarget

class Action:
    def __init__(self):
        pass
    
    def play(self) -> None:
        raise NotImplementedError("The \"play\" method is not implemented for this Action.")
    
class DealDamage(Action):
    def __init__(self, val: Value, target: CreatureTarget):
        self.val = val
        self.target = target

class GainBlock(Action):
    def __init__(self, val: Value):
        self.val = val