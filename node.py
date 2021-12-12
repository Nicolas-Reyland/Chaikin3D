#
from __future__ import annotations
import connection as C
from dataholders import VirtualSet
import numpy as np


class Node:
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z
        self.num_connections: int = 0
        self.connection_list: list[C.Connection] = []
        self.coords = np.array([self.x, self.y, self.z])

    def __eq__(self, other: Node) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self) -> str:
        return f"[({self.x:.2f},{self.y:.2f},{self.z:.2f}); num_connections = {self.num_connections}]"

    def __repr__(self):
        return str(self)

    def connect(self, other: Node, type_: str):
        # check connection validity
        if C.Connection.are_connected(self, other, "any"):
            return
        assert type_ == "main" or type_ == "graphical", f"Invalid connection type: {type_}"
        # create connection
        conn = C.Connection(self, other, type_)
        # add to self
        self.connection_list.append(conn)
        self.num_connections += 1
        # add to other
        other.connection_list.append(conn)
        other.num_connections += 1

    def get_connections_by_type(self, type_: str):
        if type_ == "any":
            return self.connection_list
        return list(filter(lambda conn: conn.type_ == type_, self.connection_list))

    def get_triangles(self, type_: str = "any") -> VirtualSet:
        triangles = VirtualSet()
        for conn in self.get_connections_by_type(type_):
            # find the other, "partner", node in the connection
            conn_node = conn.get_partner_node(self)
            # find triangular connection_list
            for sub_conn in filter(
                lambda sub_conn: not sub_conn.contains_node(self),
                conn_node.get_connections_by_type(type_),
            ):
                sub_conn_node = sub_conn.get_partner_node(conn_node)
                if C.Connection.are_connected(sub_conn_node, self, type_):
                    triangles.add(
                        Triangle(self.coords, conn_node.coords, sub_conn_node.coords)
                    )
        return triangles

    def get_node_triplets(self, type_: str = "any") -> list[list[Node]]:
        triangles = []
        for conn in self.get_connections_by_type(type_):
            # find the other, "partner", node in the connection
            conn_node = conn.get_partner_node(self)
            # find triangular connection_list
            for sub_conn in filter(
                lambda sub_conn: not sub_conn.contains_node(self),
                conn_node.get_connections_by_type(type_),
            ):
                sub_conn_node = sub_conn.get_partner_node(conn_node)
                if C.Connection.are_connected(sub_conn_node, self, type_):
                    triangles.append(
                        [self, conn_node, sub_conn_node]  #! CHANGE TO SET ?
                    )
        return triangles

    @staticmethod
    def from_point(point: list[float]) -> Node:
        assert len(point) == 3
        return Node(point[0], point[1], point[2])


class Triangle:
    def __init__(self, A: np.array[float], B: np.array[float], C: np.array[float]):
        self.data = [A.tolist(), B.tolist(), C.tolist()]

    def __str__(self) -> str:
        return (
            "{"
            + ", ".join(
                map(
                    str,
                    sorted(self.data, key=lambda tr: tr[0] * 3 + tr[1] * 5 + tr[2] * 7),
                )
            )
            + "}"
        )

    def __eq__(self, other: Triangle) -> bool:
        return (
            self.data[0] in other.data
            and self.data[1] in other.data
            and self.data[2] in other.data
        )

    def __getitem__(self, index: int) -> list[float]:
        return self.data[
            index
        ]  # order should not be important. One should always read the whole data

    def __iter__(self):
        return iter(self.data)


#
