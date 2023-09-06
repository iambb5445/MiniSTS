from typing import TypeVar, Generic
from typing import Callable
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
        self.index = (self.index + 1) % len(self.values)
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

class UserInput:
    @staticmethod
    def ask_for_number(ask: str, condition: Callable[[int], bool] = lambda _: True) -> int:
        while(True):
            try:
                inp = int(input(ask))
                if condition(inp):
                    return inp
                else:
                    print("Invalid value")
            except ValueError:
                print("Please enter an integer value.")
    @staticmethod
    def ask_for_bool(ask: str, yes_default: bool) -> bool:
        while(True):
            inp = input(ask + ("[Y/n]" if yes_default else "y/N"))
            if inp == "":
                return True if yes_default else False
            elif inp in ["y", "Y"]:
                return True
            elif inp in ["n", "N"]:
                return False
            else:
                print("Invalid value\nPlease enter one of [n or N for no] or [y or Y for yes].")