#from typing import TypeVar, Generic

class Value():
    def __init__(self):
        self.upgrade_count = 0

    def get(self) -> int:
        raise NotImplementedError("The \"get\" method is not defined for this Value.")

    def upgrade(self, times: int) -> None:
        self.upgrade_count += times
    
class ConstValue(Value):
    def __init__(self, val: int):
        self.val = val
    
class Upgradable(Value):
    def __init__(self, val: int, upgraded: int, threshold: int = 1):
        super().__init__()
        self.val = val
        self.upgraded = upgraded
        self.threshold = threshold
    
    def get(self) -> int:
        return self.val if self.upgrade_count < self.threshold else self.upgraded

class LinearUpgradable(Value):
    def __init__(self, val: int, step: int, threshold: int = 1):
        self.val = val
        self.step = step
        self.threshold = threshold
    
    def get(self) -> int:
        return self.val + self.step * int(self.upgrade_count/self.threshold)