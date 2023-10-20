from __future__ import annotations
import random

# Question: do we want to differentiate between CardValue and regular Value? Since only card value should be upgradable!

class Value():
    def get(self) -> int:
        raise NotImplementedError("The \"get\" method is not defined for {}.".format(self.__class__.__name__))
    
    def peek(self):
        return self.get()

    def negative(self) -> Value:
        raise NotImplementedError("The \"negative\" method is not defined for {}.".format(self.__class__.__name__))
    
    def upgrade(self, times: int) -> None:
        pass
    
    def __repr__(self) -> str:
        return str(self.peek())
    
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
        assert self.begin < self.end, "Begin ({}) cannot be greater than or equal to end ({}).".format(self.begin, self.end)
        self.value: int = 0
        self.peeked = False
    
    def get(self):
        value = self.peek()
        self.peeked = False
        return value
    
    def peek(self):
        if not self.peeked:
            self.value = random.randrange(self.begin, self.end)
        return self.value

    def negative(self) -> RandomUniformRange:
        return RandomUniformRange(self.end * -1, self.begin * -1)