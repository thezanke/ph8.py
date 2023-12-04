from collections import OrderedDict
from typing import Any


class LRUCache(OrderedDict):
    def __init__(self, capacity=500):
        super().__init__()
        assert capacity > 0, "Capacity must be positive"
        self.capacity = capacity

    def get(self, key: str):
        try:
            value = self[key]
            self.move_to_end(key)

            return value
        except KeyError:
            return None

    def add(self, key: str, value: Any):
        self[key] = value
        self.move_to_end(key)

        if len(self) > self.capacity:
            self.popitem(last=False)
