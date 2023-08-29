from typing import TypeVar, Generic
import random

T = TypeVar("T")

class ItemSet(Generic[T]):
    def get(self) -> T:
        raise NotImplementedError("The \"get\" method is not implemented for this ActionSet.")

class RoundRobinCore(ItemSet[T]):
    def __init__(self, *values: T):
        self.values = [t for t in values]
        self.index = 0
        self.reset()

    def reset(self) -> None:
        raise NotImplementedError("The \"reset\" method is not implemented for this RoundRobin.")
    
    def get(self) -> T:
        ret = self.values[self.index]
        return ret

class RoundRobin(RoundRobinCore[T]):
    def __init__(self, start: int, *values: T):
        self.start = start
        super().__init__(*values)
    
    def reset(self):
        self.index = self.start

class RoundRobinRandomStart(RoundRobinCore[T]):
    def reset(self):
        self.index = random.randrange(0, len(self.values))