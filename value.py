#from typing import TypeVar, Generic
import random

class Value():
    def __init__(self):
        pass
    
    def get(self) -> int:
        raise NotImplementedError("The \"get\" method is not defined for this Value.")
    
class ConstValue(Value):
    def __init__(self, val: int):
        self.val = val

class Upgradable(Value):
    def __init__(self):
        self.upgrade_count = 0

    def upgrade(self, times: int) -> None:
        self.upgrade_count += times
    
class UpgradableOnce(Upgradable):
    def __init__(self, val: int, upgraded: int, threshold: int = 1):
        super().__init__()
        self.val = val
        self.upgraded = upgraded
        self.threshold = threshold
    
    def get(self) -> int:
        return self.val if self.upgrade_count < self.threshold else self.upgraded

class LinearUpgradable(Upgradable):
    def __init__(self, val: int, step: int, threshold: int = 1):
        self.val = val
        self.step = step
        self.threshold = threshold
    
    def get(self) -> int:
        return self.val + self.step * int(self.upgrade_count/self.threshold)
    
class RandomUniformRange(Value):
    def __init__(self, begin: int, end: int):
        self.begin = begin
        self.end = end
    
    def get(self):
        return random.randrange(self.begin, self.end)