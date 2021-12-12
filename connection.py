#
from __future__ import annotations
import node as N


class Connection:
    """
    Connection between two Nodes.

    """

    def __init__(self, A: N.Node, B: N.Node, type_: str):
        self.A: N.Node = A
        self.B: N.Node = B
        self.type_: str = type_  # 'main', 'graphical'

    def __eq__2(self, other: Connection) -> bool:
        return self.A == other.A and self.B == other.B and self.type_ == other.type_

    def __str__(self) -> str:
        return f"A: {self.A} -> B: {self.B} type: {self.type_}"

    def contains_node(self, node: N.Node) -> bool:
        """
        Is the node 'node' part of this connection ?

        Args:
            node (Node): Node which can be part of this connection.

        Returns:
            bool: The node is part of this connection.

        """

        return self.A == node or self.B == node

    def get_partner_node(self, node: N.Node) -> N.Node:
        """
        Return the partner node.

        A Connection being made of two nodes, return the node that is NOT 'node'.

        Args:
            node (Node): Node we know of (we don't want this one back).

        Returns:
            Node: The partner node.

        Raises:
            AssertionError: The node 'node' is not part of this connection

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
        The 'old_partner' becomes the 'new_partner' in this Connection.

        If A (resp. B) is 'old_partner', A (resp. B) will become 'new_partner'.

        Args:
            old_partner (Node): Node existing in this connection.
            new_partner (Node): Node that will be part of this connection.

        Raises:
            AssertionError: The 'old_partner' is not part of this Connection.

        """

        if self.A == old_partner:
            self.A = new_partner
        else:
            assert self.B == old_partner
            self.B = new_partner

    @staticmethod
    def connection_list_contains_node(
        connection_list: list[Connection], node: N.Node, type_: str = "main"
    ) -> bool:
        """
        The given list of connections contains (A or B) the given node.

        The by-connection-type-filtered list of connections does contains, should
        it be the A-Node or B-Node, ths given Node 'node'.

        Args:
            connection_list (list[Connection]): List of connections to look through.
            node            (Node)            : The node to look for.
            type_           (str)             : The type of connections to look into.

        Returns:
            bool: The given list of connections contains (A or B) the given node.

        """

        if type_ == "any":
            return any([conn.A == node or conn.B == node for conn in connection_list])
        return any(
            [
                conn.type_ == type_ and (conn.A == node or conn.B == node)
                for conn in connection_list
            ]
        )

    @staticmethod
    def connection_list_contains_connection(
        connection_list: list[Connection], connection: Connection
    ) -> bool:
        """
        Does the list of connections contains the 'connection' ?

        Args:
            connection_list (list[Connection]): List of connections.
            connection      (Connection)      : Connection to llok for.

        Returns:
            bool: The list of connections contains the 'connection'.

        """

        return any(
            [
                conn.A == connection.A
                and conn.B == connection.B
                or conn.B == connection.A
                and conn.A == connection.B
                for conn in connection_list
            ]
        )

    @staticmethod
    def are_connected(node1: N.Node, node2: N.Node, type_: str = "main") -> bool:
        """
        Is 'node1' connected to 'node2' with a connection of type 'tpye_' ?

        Args:
            node1 (Node): First Node.
            node2 (Node): Second Node.
            type_ (str) : Type of connections to look into.

        Returns:
            bool: Are the two nodes 'type_'-connected ?

        """

        return Connection.connection_list_contains_node(
            node1.connection_list, node2, type_
        )

    @staticmethod
    def get_connection_with_node(
        connection_list: list[Connection], node: N.Node
    ) -> Connection:
        """
        Find any connection that contains 'node' and return it.

        Args:
            connection_list (list[Connection]): List of connections.
            node            (Node)            : Node to look for in the list.

        Returns:
            Connection: The connection that binds 'node' and another node (first found).

        Raises:
            Exception: No connection with node 'node' in the given list 'connection_list'

        """

        for conn in connection_list:
            if conn.contains_node(node):
                return conn
        raise Exception(
            f"No connection with node {node} in the given list: {connection_list}"
        )
