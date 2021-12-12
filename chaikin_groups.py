# Chaikin3D - Groups module
from __future__ import annotations
from collections.abc import Iterable
import connection as C
import node as N
from dataholders import VirtualSet
import numpy, matrix


class Group:
    """
    A Chaikin Group is a collection of nodes that make up a face in a mesh.

    A Chaikin Group is a collection of nodes that make up a face in a polyhedron.
    All the nodes in a group share the same 2D plane. When ordered in a circle-like
    list, the group is called an Ordered Group (OGroup). When applying the Chaikin3D
    algorithm to a mesh, new Groups appear. Each node of the the mesh is the
    source of one new Group in the final mesh. All existing Groups see their size
    (number of nodes) double. When a node gives birth to a Chaikin Group, its size
    is equal to the number of (main-)connections of that node (at least 3).

    Once ordered, a the graphical connections can easily be made (see 'inter_connect').
    To order a group, once must be sure of having added all the nodes that correspond
    to the specific face.

    """

    def __init__(self, iterable: Iterable, do_order: bool = False):
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
        """
        Order a Group.

        Order a Group based on node inter-connectivity. We start be taking a
        node (any node), and looking for nodes in this Group in its main connections.
        Once such a node/connection is found, we can propagate to this node, until
        we meet the starting node.
        Sets the 'ordered' attribtue to True.

        Args:
            force (bool):
                force the ordering algorithm, even tho the 'ordered'
                attribute is set to True.

        Raises:
            Exception: Broken Group (the nodes do not form a face).

        """

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
                    f"Warning: broken group found. attaching remaning nodes: {len(group_list)}"
                )
                self.ogroup.extend(group_list)
                raise Exception("Broken group (see stdout for more info)")

        self.ordered = True

    def cycle_connect(self, connection_type: str = "main") -> None:
        """
        Connect the nodes the Group in a circular manner.

        The Group must an OGroup (ordered Group). Because of this, we can simply
        navigate through the ordered list of nodes (which is ordered by
        node-connections) and connect the nodes with their neighbours in the
        OGroup.

        Args:
            connection_type (str): Connection type: "main" or "graphical".

        Raises:
            AssertionError: The Group is NOT ordered (call 'order' first).

        """

        assert not self.ordered, f"Group is not ordered: {self}"

        for i in range(self.size - 1):
            self.group[i].connect(self.group[i + 1], connection_type)
        self.group[-1].connect(self.group[0], connection_type)

    def inter_connect(
        self, connection_type: str = "graphical", order_first: bool = False
    ) -> None:
        """
        Create the required graphical connections between the nodes.

        Create the required graphical connections between the nodes in a way
        that the smallest amount of connections is created.

        Args:
            connection_type (str) : Connection type: "main" or "graphical".
            order_first     (bool): Call the 'order' method first ?

        Raises:
            AssertionError: The Group is NOT ordered (maybe set 'order_first' to True).

        """

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


def _debug_print_full_node(node, num_tabs=0):
    prefix = "\t" * num_tabs
    print(f"{prefix}{str(node)}:")
    print(f"{prefix} main :")
    for conn in node.get_connections_by_type("main"):
        print(f"{prefix}\t - {str(conn)}")
    print(f"{prefix} graphical :")
    for conn in node.get_connections_by_type("graphical"):
        print(f"{prefix}\t - {str(conn)}")


def _debug_print_full_nodes(nodes, num_tabs=0):
    prefix = "\t" * num_tabs
    print(f"{prefix}Num nodes: {len(nodes)}")
    for node in nodes:
        _debug_print_full_node(node, num_tabs + 1)
        print()


#
