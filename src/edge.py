#
from __future__ import annotations
import node as N


class Edge:
    """
    Edge between two Nodes.

    """

    def __init__(self, A: N.Node, B: N.Node, type_: str):
        self.A: N.Node = A
        self.B: N.Node = B
        self.type_: str = type_  # 'main', 'graphical'

    def __eq__(self, other: Edge) -> bool:
        return self.type_ == other.type_ and (self.A, self.B) in [
            (other.A, other.B),
            (other.B, other.A),
        ]

    def __iter__(self):
        return iter((self.A, self.B))

    def __str__(self) -> str:
        return f"A: {self.A} -> B: {self.B} type: {self.type_}"

    def __repr__(self) -> str:
        return str(self)

    def contains_node(self, node: N.Node) -> bool:
        """
        Is the node 'node' part of this edge ?

        Args:
            node (Node): Node which can be part of this edge.

        Returns:
            bool: The node is part of this edge.

        """

        return self.A == node or self.B == node

    def get_partner_node(self, node: N.Node) -> N.Node:
        """
        Return the partner node.

        A Edge being made of two nodes, return the node that is NOT 'node'.

        Args:
            node (Node): Node we know of (we don't want this one back).

        Returns:
            Node: The partner node.

        Raises:
            AssertionError: The node 'node' is not part of this edge

        """

        # partner is B
        if self.A == node:
            assert self.B != node
            return self.B
        # partner is A
        assert self.B == node
        return self.A

    def update_node(self, old_partner: N.Node, new_partner: N.Node) -> None:
        """
        The 'old_partner' becomes the 'new_partner' in this Edge.

        If A (resp. B) is 'old_partner', A (resp. B) will become 'new_partner'.

        Args:
            old_partner (Node): Node existing in this edge.
            new_partner (Node): Node that will be part of this edge.

        Raises:
            AssertionError: The 'old_partner' is not part of this Edge.

        """

        if self.A == old_partner:
            self.A = new_partner
        else:
            assert self.B == old_partner
            self.B = new_partner

    @staticmethod
    def edge_list_contains_node(
        edge_list: list[Edge], node: N.Node, type_: str = "main"
    ) -> bool:
        """
        The given list of edges contains (A or B) the given node.

        The by-edge-type-filtered list of edges does contains, should
        it be the A-Node or B-Node, ths given Node 'node'.

        Args:
            edge_list (list[Edge]): List of edges to look through.
            node            (Node)            : The node to look for.
            type_           (str)             : The type of edges to look into.

        Returns:
            bool: The given list of edges contains (A or B) the given node.

        """

        if type_ == "any":
            return any(edge.A == node or edge.B == node for edge in edge_list)
        return any(
            edge.type_ == type_ and (edge.A == node or edge.B == node)
            for edge in edge_list
        )

    @staticmethod
    def edge_list_contains_edge(edge_list: list[Edge], edge: Edge) -> bool:
        """
        Does the list of edges contains the 'edge' ?

        Args:
            edge_list (list[Edge]): List of edges.
            edge      (Edge)      : Edge to llok for.

        Returns:
            bool: The list of edges contains the 'edge'.

        """

        return edge in edge_list

        return any(
            conn.A == edge.A
            and conn.B == edge.B
            or conn.B == edge.A
            and conn.A == edge.B
            for conn in edge_list
        )

    @staticmethod
    def are_connected(node1: N.Node, node2: N.Node, type_: str = "main") -> bool:
        """
        Is 'node1' connected to 'node2' with a edge of type 'tpye_' ?

        Args:
            node1 (Node): First Node.
            node2 (Node): Second Node.
            type_ (str) : Type of edges to look into.

        Returns:
            bool: Are the two nodes 'type_'-connected ?

        """

        return Edge.edge_list_contains_node(node1.edge_list, node2, type_)

    @staticmethod
    def get_edge_with_node(edge_list: list[Edge], node: N.Node) -> Edge:
        """
        Find any edge that contains 'node' and return it.

        Args:
            edge_list (list[Edge]): List of edges.
            node            (Node)            : Node to look for in the list.

        Returns:
            Edge: The edge that binds 'node' and another node (first found).

        Raises:
            Exception: No edge with node 'node' in the given list 'edge_list'

        """

        for conn in edge_list:
            if conn.contains_node(node):
                return conn
        raise Exception(f"No edge with node {node} in the given list: {edge_list}")
