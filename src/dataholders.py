#
from __future__ import annotations


class VirtualDict:
    """
    VirtualDict is like the dict class, but can store non-hashable types as keys.
    Because of this, it is much slower.

    """

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
        """
        Returns the list of keys.

        Returns:
            list: List of keys.

        """

        return self.key_list

    def values(self):
        """
        Returns the list of values.

        Returns:
            list: List of values.

        """

        return self.value_list

    def contains_key(self, key) -> bool:
        """
        Does this VirtualDict contain the 'key' key ?

        Args:
            key (str): Key to look for.

        Returns:
            bool: The key is stored in the VirtualDict's keys.

        """

        return key in self.key_list

    def contains_value(self, value) -> bool:
        """
        Does this VirtualDict contain the 'value' value ?

        Args:
            value (str): Value to look for.

        Returns:
            bool: The value is stored in the VirtualDict's values.

        """

        return value in self.value_list


class VirtualSet:
    """
    VirtualSet is like the set class, but can store non-hashable types.
    Because of this, it is much slower.

    """

    def __init__(self, iterable=None):
        self.data = []
        if iterable:
            if type(iterable) == VirtualSet or type(iterable) == set:
                self.data = list(iterable)
            else:
                for value in iterable:
                    if value not in self.data:
                        self.data.append(value)
                    else:
                        # print("Warning: doublon in VirtualSet initial-data iterable")
                        pass
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

    def __and__(self, other_set: VirtualSet) -> VirtualSet:
        """
        Intersection for VirtualSet.

        Args:
            other_set (VirtualSet): Other virtual set.

        """

        return VirtualSet(element for element in other_set if element in self)

    def __or__(self, other_set: VirtualSet) -> VirtualSet:
        """
        Union for VirtualSet.

        Args:
            other_set (VirtualSet): Other virtual set.

        """

        return VirtualSet(self.data + other_set.data)

    def __sub__(self, other_set: VirtualSet) -> VirtualSet:
        """
        Subtraction for VirtualSet.

        Args:
            other_set (VirtualSet): Other virtual set.

        """

        return VirtualSet(element for element in self if element not in other_set)

    def add(self, value, verify: bool = True) -> None:
        """
        Add the 'value' to the VirtualSet.

        Args:
            value  (_)   : Value to add to the VirtualSet.
            verify (bool):
                Verify that the value is not inside the Set before adding it ?
                Because of non-hashable nature of the values stored in this Set,
                we must manually verify an item's unicity. You can disable this
                if you are sure that the item is not inside the VirtualSet by
                setting the 'verify' argument to False.

        """

        if not verify or value not in self.data:
            self.data.append(value)
            self.size += 1
            return True
        return False

    def pop(self):
        """
        Pop any item out of this VirtualSet.

        Returns:
            _: The popped item.

        """

        return self.data.pop()

    def copy(self):
        """
        Returns a copy of this VirtualSet. The individual items are not copied
        if they themselves are objects.

        Returns:
            VirtualSet: Copy of this VirtualSet.

        """

        virtual_set_copy = VirtualSet()
        virtual_set_copy.data = self.data.copy()
        virtual_set_copy.size = self.size
        return virtual_set_copy


#
