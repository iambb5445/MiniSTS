from typing import TypeVar, Generic
from typing import Callable
import random

T = TypeVar("T")

class ItemSet(Generic[T]):
    class NoItemsAvailableExeption(Exception):
        pass

    def __init__(self):
        self.cur: T|None = None

    def _sample(self) -> T:
        raise NotImplementedError("The \"_sample\" method is not implemented for {}.".format(self.__class__.__name__))
    
    def get(self) -> T:
        ret = self.peek()
        self.cur = None
        return ret

    def peek(self) -> T:
        self.cur = self.cur if self.cur is not None else self._sample()
        return self.cur

class RoundRobinCore(ItemSet[T]):
    def __init__(self, *values: T):
        super().__init__()
        self.values = [t for t in values]
        self.index = 0
    
    def _sample(self) -> T:
        ret = self.values[self.index]
        self.index = (self.index + 1) % len(self.values)
        return ret

class RoundRobin(RoundRobinCore[T]):
    def __init__(self, start: int, *values: T):
        super().__init__(*values)
        self.index = start

class RoundRobinRandomStart(RoundRobinCore[T]):
    def __init__(self, *values: T):
        super().__init__(*values)
        self.index = random.randrange(0, len(self.values))

class ItemSequence(ItemSet[T]):
    def __init__(self, *item_sets: ItemSet[T]|T):
        super().__init__()
        self.item_set_list: list[ItemSet[T]|T] = [item_set for item_set in item_sets]
        self.index = 0
    
    def _sample(self) -> T:
        while self.index < len(self.item_set_list):
            try:
                value:T|ItemSet[T] = self.item_set_list[self.index]
                if isinstance(value, ItemSet):
                    item_set: ItemSet[T] = value
                    return item_set.get()
                else:
                    self.index += 1
                    return value
            except ItemSet.NoItemsAvailableExeption as _:
                self.index += 1
        raise ItemSet.NoItemsAvailableExeption()

class RandomizedItemSet(ItemSet[T]):
    def __init__(self, *values_and_weights: tuple[T, float]):
        super().__init__()
        self.values: list[T] = [t[0] for t in values_and_weights]
        self.weights: list[float] = [t[1] for t in values_and_weights]

    def _sample(self) -> T:
        return random.choices(self.values, weights=self.weights)[0]

class PreventRepeat(ItemSet[T]):
    MAX_TRIES = 100

    def __init__(self, wrapped: ItemSet[T], invalid_item: T, invalid_count: int, consecutive: bool):
        super().__init__()
        self.wrapped = wrapped
        self.invalid_item = invalid_item
        self.invalid_count = invalid_count
        self.counter: int = 0
        self.consecutive = consecutive
    
    def _sample(self) -> T:
        for _ in range(PreventRepeat.MAX_TRIES):
            ret = self.wrapped.get()
            if ret == self.invalid_item:
                self.counter += 1
                if self.counter >= self.invalid_count:
                    continue
            else:
                if self.consecutive:
                    self.counter = 0
            return ret
        raise ItemSet.NoItemsAvailableExeption()
    
class PreventRepeats(ItemSet[T]):
    def __init__(self, wrapped: ItemSet[T], *invalids: tuple[T, int], consecutive: bool):
        super().__init__()
        self.wrapped = wrapped
        for invalid in invalids:
            invalid_item, invalid_count = invalid
            self.wrapped = PreventRepeat(self.wrapped, invalid_item, invalid_count, consecutive)

    def _sample(self) -> T:
        return self.wrapped.get()

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

class Broadcast:
    def __init__(self):
        self.listeners = {}

    def subscribe(self):
        pass