# Chaikin3D - Groups module
from __future__ import annotations
import connection as C
import node as N
from dataholders import VirtualSet
import numpy, matrix


class Group:
    def __init__(self, iterable, do_order: bool = False):
        self.group: VirtualSet[N.Node] = VirtualSet(iterable)
        self.ogroup = None
        self.ordered = False
        self.size = self.group.size
        # assert self.size > 2 # >= 3
        if do_order:
            self.order()

    def __str__(self) -> str:
        return "[{}] o: {} s: {}".format(
            ", ".join(map(str, self.group)), self.ordered, self.size
        )

    def __repr__(self) -> str:
        return str(self)

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.ogroup) if self.ordered else iter(self.group)

    def __getitem__(self, index: int):
        if self.ordered:
            return self.ogroup[index]
        return self.group[index]

    def order(self, force: bool = False) -> None:
        if not force and self.ordered:
            return
        # trivial case
        if self.size < 3:
            self.ogroup = self.group
            self.ordered = True
            return
        # initialize variables
        group_list: list[N.Node] = list(self.group)
        current_node = group_list.pop(0)
        self.ogroup = [current_node]
        # connect the next ones (don't care if we go 'left' or 'right')
        while group_list:
            for remaining_node in group_list:
                if C.Connection.are_connected(current_node, remaining_node, "main"):
                    self.ogroup.append(remaining_node)
                    group_list.remove(remaining_node)
                    current_node = remaining_node
                    break
            else:
                print("current_node")
                _debug_print_full_node(current_node)
                print("group_list")
                _debug_print_full_nodes(group_list)
                print("ordered group")
                _debug_print_full_nodes(self.ogroup)
                print("group")
                _debug_print_full_nodes(self.group)
                # raise Exception('broken group')
                print(
                    "Warning: broken group found. attaching remaning nodes: {}".format(
                        len(group_list)
                    )
                )
                self.ogroup.extend(group_list)
                break

        self.ordered = True

    def cycle_connect(self, connection_type: str = "main") -> None:
        assert not self.ordered
        for i in range(self.size - 1):
            self.group[i].connect(self.group[i + 1], connection_type)
        self.group[-1].connect(self.group[0], connection_type)

    def inter_connect(
        self, connection_type: str = "graphical", order_first: bool = False
    ) -> None:
        if order_first:
            self.order(True)
        assert self.ordered
        num_iter = int(matrix.np.log2(self.size)) - 1
        #
        for x in range(num_iter):
            step = 2 ** (x + 1)
            # print('step:', step)
            prev_node = self.ogroup[0]
            for i in range(step, self.size, step):
                current_node = self.ogroup[i]
                prev_node.connect(current_node, connection_type)
                prev_node = current_node
            # connect last one to first one
            self.ogroup[0].connect(prev_node, connection_type)
