#
from __future__ import annotations


class VirtualDict:
    def __init__(self, iterable=[]):
        self.key_list = []
        self.value_list = []
        self.size = 0
        for key, value in iterable:
            self[key] = value

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(
            map(lambda i: (self.key_list[i], self.value_list[i]), range(self.size))
        )

    def __setitem__(self, key, value):
        if key in self.key_list:
            self.value_list[self.key_list.index(key)] = value
        else:
            self.key_list.append(key)
            self.value_list.append(value)
            self.size += 1

    def __getitem__(self, key):
        index = self.key_list.index(key)
        return self.value_list[index]

    def keys(self):
        return self.key_list

    def values(self):
        return self.value_list

    def contains_key(self, key) -> bool:
        return key in self.key_list

    def contains_value(self, value) -> bool:
        return value in self.value_list


class VirtualSet:
    def __init__(self, iterable=[]):
        self.data = []
        if iterable:
            if type(iterable) == VirtualSet or type(iterable) == set:
                self.data = list(iterable)
            else:
                for value in iterable:
                    if value not in self.data:
                        self.data.append(value)
                    else:
                        print("Warning: doublon in VirtualSet initial-data iterable")
        self.size = len(self.data)

    def __str__(self):
        return "v{" + ", ".join(map(str, self.data)) + "}v"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index: int):
        return self.data[index]

    def __eq__(self, other: VirtualSet) -> bool:
        for element in self.data:
            if element not in other.data:
                return False
        return True

    def add(self, value, verify: bool = True) -> bool:
        if not verify or value not in self.data:
            self.data.append(value)
            self.size += 1

    def pop(self):
        return self.data.pop(0)

    def copy(self):
        return VirtualSet(self)


#
