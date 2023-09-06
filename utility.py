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
    def ask_for_number(ask: str, condition: Callable[[int], bool]):
        inp = input(ask)
        while(True):
            try:
                inp_int = int(inp)
                if condition(inp_int):
                    return inp_int
                else:
                    print("Invalid value")
            except ValueError:
                print("Please enter an integer value.")
    '''
    @staticmethod
    def get_val_in_list(ask: str, val_list: list[T], condition: Callable[[T], bool]):
        list_ask = '\nEnter the index. Options:' + '\n'.join()
        UserInput.ask_for_number(ask + , )'''