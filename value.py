from __future__ import annotations
import random

# Question: do we want to differentiate between CardValue and regular Value? Since only card value should be upgradable!

class Value():
    def get(self) -> int:
        raise NotImplementedError("The \"get\" method is not defined for {}.".format(self.__class__.__name__))

    def negative(self) -> Value:
        raise NotImplementedError("The \"negative\" method is not defined for {}.".format(self.__class__.__name__))
    
class ConstValue(Value):
    def __init__(self, val: int):
        self.val = val
    
    def get(self):
        return self.val
    
    def negative(self) -> ConstValue:
        return ConstValue(self.val * -1)

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

    def negative(self) -> UpgradableOnce:
        return UpgradableOnce(self.val * -1, self.upgraded * -1, self.threshold)

class LinearUpgradable(Upgradable):
    def __init__(self, val: int, step: int, threshold: int = 1):
        self.val = val
        self.step = step
        self.threshold = threshold
    
    def get(self) -> int:
        return self.val + self.step * int(self.upgrade_count/self.threshold)

    def negative(self) -> LinearUpgradable:
        return LinearUpgradable(self.val * -1, self.step * -1, self.threshold)
    
class RandomUniformRange(Value):
    def __init__(self, begin: int, end: int):
        self.begin = begin
        self.end = end
    
    def get(self):
        return random.randrange(self.begin, self.end)

    def negative(self) -> LinearUpgradable:
        return LinearUpgradable(self.end * -1, self.begin * -1)