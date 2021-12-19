#
from __future__ import annotations
import edge as E
from dataholders import VirtualSet
import numpy as np


class Node:
    """
    A Node is a point in space, at the corner of a mesh.

    """

    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z
        self.coords_list = [x, y, z]
        self.coords = np.array(self.coords_list)
        self.num_edges: int = 0
        self.edge_list: list[E.Edge] = list()

    def __eq__(self, other: Node) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self) -> str:
        return (
            f"[({self.x:.2f},{self.y:.2f},{self.z:.2f}); num_edges = {self.num_edges}]"
        )

    def __repr__(self):
        return str(self)

    def connect(self, other: Node, type_: str) -> None:
        """
        Connect this Node with the 'other' node.

        Args:
            other (Node): Node to connect with.
            type_  (str): Type of the edge.

        Raises:
            AssertionError: Invalid edge type.

        """

        # check edge validity
        if E.Edge.are_connected(self, other, "any"):
            return
        assert type_ == "main" or type_ == "graphical", f"Invalid edge type: {type_}"
        # create edge
        edge = E.Edge(self, other, type_)
        # add to self
        self.edge_list.append(edge)
        self.num_edges += 1
        # add to other
        other.edge_list.append(edge)
        other.num_edges += 1

    def get_edges_by_type(self, type_: str) -> list[Edge]:
        """
        Returns the edge list of this Node, filtered by type.

        If the type_ is "any", return all the edges of this Node.

        Args:
            type_ (str): Type of edge.

        Returns:
            list[Edge]: List of edges that have the specified type.

        """

        if type_ == "any":
            return self.edge_list
        return list(filter(lambda edge: edge.type_ == type_, self.edge_list))

    def get_triangles(self, type_: str = "any") -> VirtualSet[Triangle]:
        """
        Returns the set of triangles that this Node is part of.

        Args:
            type_ (str): Type of the edges that should form the triangles.

        Returns:
            VirtualSet[Triangle]:
                VirtualSet of triangles that this Node is part of.
                The triangles are made of edges with type 'type_'.

        """

        triangles = VirtualSet()
        for edge in self.get_edges_by_type(type_):
            # find the other, "partner", node in the edge
            edge_node = edge.get_partner_node(self)
            # find triangular edge_list
            for sub_edge in filter(
                lambda sub_edge: not sub_edge.contains_node(self),
                edge_node.get_edges_by_type(type_),
            ):
                sub_edge_node = sub_edge.get_partner_node(edge_node)
                if E.Edge.are_connected(sub_edge_node, self, type_):
                    triangles.add(
                        Triangle(self, edge_node, sub_edge_node)
                    )
        return triangles

    def _own_edges_in_triangle(self, triangle: Triangle) -> tuple[E.Edge]:
        """
        Returns a list of the edges that this node is connected to, that are
        also present in the triangle.

        This node should be part of the triangle in the first place. The list
        that is returned will have exactly two edges. This is because one node
        has exactly two edges that it is part of in a triangle (made of three
        nodes).

        Args:
            triangle (Triangle): The triangle you are looking for edges in.

        Returns:
            tuple[Edge]:
                Tuple of edges that connect this node to other nodes
                in the given triangle.

        Raises:
            Exception: This node is not part of the triangle.

        """

        first_edge = None
        count: int = 0
        for edge in self.edge_list:
            other_node_coords = edge.get_partner_node(self).coords_list
            if other_node_coords in triangle:
                if first_edge is None:
                    first_edge = edge
                    continue
                else:
                    return (first_edge, edge)
                break

        # Should only find exactly two edges
        raise Exception(
            f"This node is not part of the triangle? Node: {self},"
            f" Triangle: {triangle}."
        )

    def order_edges(self, duplicate_triangles: VirtualSet = None) -> VirtualSet:
        """
        Order all the edges this node is part of.

        The edges can be ordered such that when iterating over them in pairs,
        you directly get the pairs of edges per triangle this node is connected to.
        This is achieved by getting all the triangles this node is connected to
        (all those triangles must form a cycled mesh part) and ordering those.
        Once ordered, the edges can be read in an ordered way.

        Args:
            type_ (str): Tye of the edges.

        Returns:
            VirtualSet[Triangle]: Set of removed triangles during reduction.

        Raises:
            Exception: Invalid/Corrupted Node/Polyhedron.

        """

        if duplicate_triangles is None:
            duplicate_triangles = VirtualSet()

        # All the triangles that are connected to this node (unordered)
        raw_triangles = self.get_triangles() - duplicate_triangles

        # Get edge-participations (number of triangles an edge is part of)
        # A---------B---------C
        # |\\__     |     __// \
        # | \  \__  |  __/  /  \
        # |  \    \_|_/    /   \
        # |   \     E     /    F
        # |    \    |    /    /
        # |     \   |   /   _/
        # |      \  |  /  _/
        # |       \ | / _/
        # |        \|//
        # G---------D
        #
        # Edge 'D-A' is part of 3 triangles sharind 'D-A': {DAG, DAE, DAC}
        # Same goes for 'D-C' and {DCF, DCB, DCA}
        #
        # 'Reducing' the corresponding triangle set means to remove DAC from it

        print(f"{self = }")

        participations = list()
        for i, edge in enumerate(self.edge_list):
            partner_node_coords = edge.get_partner_node(self).coords_list
            participations.append(
                len([t for t in raw_triangles if partner_node_coords in t])
            )

        triangles, duplicate_triangles = Triangle.reduce_triangle_set(
            raw_triangles, self.edge_list, participations
        )
        triangles = list(triangles)

        # Last triangle (keeping track of the last one)
        last_triangle = triangles.pop()

        # Ordered list of the edges
        # Fill it with the two edges of the last_triangle that this node is part of
        _, popped_edge = self._own_edges_in_triangle(last_triangle)
        ordered_edge_list: list[Edge] = [popped_edge]
        last_partner_node: Node = ordered_edge_list[-1].get_partner_node(self)
        last_partner_node_coords = last_partner_node.coords_list

        # while there are triangles left ...
        while triangles:
            # ... look for the next one (and the corresponding edges)
            for index, triangle in enumerate(triangles):
                if last_partner_node_coords in triangle:
                    # found the next triangle !
                    (edge1, edge2) = self._own_edges_in_triangle(triangle)
                    if edge1.contains_node(last_partner_node):
                        # order: edge1, edge2
                        ordered_edge_list.append(edge2)
                        # prepare next iteration
                        last_partner_node = edge2.get_partner_node(self)
                    else:
                        # order: edge2, edge1
                        assert edge2.contains_node(last_partner_node)
                        ordered_edge_list.append(edge1)
                        # prepare next iteration
                        last_partner_node = edge1.get_partner_node(self)
                    # prepare next iteration through triangles
                    last_partner_node_coords = last_partner_node.coords_list
                    triangles.pop(index)
                    break
            else:
                print("official", len(self.edge_list))
                for edge in self.edge_list:
                    print(f"    {edge = }")
                print("ordered", len(ordered_edge_list))
                for edge in ordered_edge_list:
                    print(f"    {edge = }")
                rest = [e for e in self.edge_list if e not in ordered_edge_list]
                print("rest", len(rest))
                for edge in rest:
                    print(f"    {edge = }")
                print()
                raise Exception(f"Corrupt node found. Aborting. node = {self}")
        # replace class edge_list with ordered one
        self.edge_list = ordered_edge_list
        return duplicate_triangles

    @staticmethod
    def from_point(point: np.array) -> Node:
        """
        Return the Node at 'point'.

        Args:
            point (np.array): Point in space.

        Returns:
            Node: Node instance.

        Raises:
            AssertionError: The number of scalar values in the vector are not 3

        """

        assert (
            len(point) == 3
        ), f"The number of scalar values in the vector are not 3 ({len(point)} != 3)"
        return Node(point[0], point[1], point[2])


class Triangle:
    """
    Triangle/Face class. Formed by three Node coordinates.

    """

    def __init__(self, A: Node, B: Node, C: Node):
        self.data = [A.coords_list, B.coords_list, C.coords_list]

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

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Triangle) -> bool:
        return (
            self.data[0] in other
            and self.data[1] in other
            and self.data[2] in other
        )

    def __getitem__(self, index: int) -> list[float]:
        return self.data[
            index
        ]  # order should not be important. One should always read the whole data

    def __iter__(self):
        return iter(self.data)

    @staticmethod
    def reduce_triangle_set(
        triangle_set: VirtualSet[Triangle],
        edge_list: list[E.Edge],
        participations: list[int],
    ) -> tuple[VirtualSet[Triangle]]:
        """
        See doc in 'Node.order_edges' mehod

        Args:
            triangle_set   (VirtualSet[Triangle]): Set of triangles to reduce.
            edge_list      (list[E.Edge])        :
                List of edges corresponding to the given triangle set.
            participations (list[int])           :
                The nth edge is part of 'participations[n]' triangles from the
                triangle_set

        Returns:
            tuple[VirtualSet[Triangle]]:
                (Reduced triangle set, Removed triangles set)

        """

        reduced_triangle_set = triangle_set.copy()

        triangles_per_edge = list()
        for n in range(3, max(participations) + 1):
            high_part_edges = (edge for m, edge in enumerate(edge_list) if participations[m] == n)
            for edge in high_part_edges:
                c1, c2 = edge.A.coords_list, edge.B.coords_list
                triangles_per_edge.append(
                    VirtualSet(
                        filter(
                            lambda triangle: c1 in triangle and c2 in triangle,
                            reduced_triangle_set,
                        )
                    )
                )
        print(f"{triangles_per_edge = }")
        # if a triangle finds itself in two different sets, it should be removed
        vset_intersections = VirtualSet()
        for i,edge_triangle_set in enumerate(triangles_per_edge):
            for j,other_edge_triangle_set in enumerate(triangles_per_edge):
                if i == j:
                    continue
                print(f"{edge_triangle_set = }")
                print(f"{other_edge_triangle_set}")
                vset_intersection = edge_triangle_set & other_edge_triangle_set
                if vset_intersection:
                    print(f"YES {vset_intersection = }")
                reduced_triangle_set -= vset_intersection
                vset_intersections &= vset_intersection

        return reduced_triangle_set, vset_intersections
