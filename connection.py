#
from __future__ import annotations
import node as N


class Connection:
    def __init__(self, A: N.Node, B: N.Node, type_: str):
        self.A: N.Node = A
        self.B: N.Node = B
        self.type_: str = type_  # 'main', 'graphical'

    def __eq__2(self, other: Connection) -> bool:
        return self.A == other.A and self.B == other.B and self.type_ == other.type_

    def __str__(self) -> str:
        return f"A: {self.A} -> B: {self.B} type: {self.type_}"

    def contains_node(self, node: N.Node) -> bool:
        return self.A == node or self.B == node

    def get_partner_node(self, node: N.Node) -> N.Node:
        """return the other node (different from 'node') in the [self.A, self.B] list"""
        if self.A == node:
            assert self.B != node
            return self.B
        assert self.B == node
        return self.A

    def update_node(self, old_partner: N.Node, new_partner: N.Node) -> None:
        if self.A == old_partner:
            self.A = new_partner
        else:
            assert self.B == old_partner
            self.B = new_partner

    @staticmethod
    def connection_list_contains_node(
        connection_list: list[Connection], node: N.Node, type_: str = "main"
    ) -> bool:
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
        return Connection.connection_list_contains_node(
            node1.connection_list, node2, type_
        )

    @staticmethod
    def get_connection_with_node(
        connection_list: list[Connection], node: N.Node
    ) -> Connection:
        for conn in connection_list:
            if conn.contains_node(node):
                return conn
        raise Exception(
            f"No connection with node: {node} in the given list: {connection_list}"
        )
