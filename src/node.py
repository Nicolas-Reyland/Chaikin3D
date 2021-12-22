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
        T = type(other)
        if T is Node:
            return self.x == other.x and self.y == other.y and self.z == other.z
            # return self is other
        elif T is list:
            return self.coords_list == other
        elif T is tuple:
            return (self.x, self.y, self.z) == other
        elif T is np.array:
            return np.array_equal(self.coords, other)
        else:
            raise NotImplementedError(f"Type {T} is not supported for Node equality")

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
                    triangles.add(Triangle(self, edge_node, sub_edge_node))
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
            other_node = edge.get_partner_node(self)
            if other_node in triangle:
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

        participations = list()
        for i, edge in enumerate(self.edge_list):
            partner_node_coords = edge.get_partner_node(self).coords_list
            participations.append(
                len([t for t in raw_triangles if partner_node_coords in t])
            )

        triangles, duplicate_triangles = Triangle.reduce_triangle_set(
            self, raw_triangles, participations
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
        self.nodes = [A, B, C]

    def __str__(self) -> str:
        return (
            "{"
            + ", ".join(
                map(
                    str,
                    sorted(
                        self.iter_coords,
                        key=lambda tr: tr[0] * 3 + tr[1] * 5 + tr[2] * 7,
                    ),
                )
            )
            + "}"
        )

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Triangle) -> bool:
        return (
            self.nodes[0] in other and self.nodes[1] in other and self.nodes[2] in other
        )

    def __getitem__(self, index: int) -> list[float]:
        # order ('absolute' numerical value of index) should not be important.
        return self.nodes[index]

    def __iter__(self):
        return iter(self.nodes)

    @property
    def sim_hash(self):
        # Give a NON-UNIQUE hash for this triangle
        # The goal is to return a value that is as unique as possible
        # This is used for optimization.
        return sum(sum(node.coords + i + 1) for i, node in enumerate(self.nodes))

    @property
    def iter_coords(self):
        return iter(map(lambda node: node.coords_list, self))

    @staticmethod
    def reduce_triangle_set(
        node: Node,
        triangle_set: VirtualSet[Triangle],
        participations: list[int],
    ) -> tuple[VirtualSet[Triangle]]:
        """
        See doc in 'Node.order_edges' mehod

        Args:
            node           (Node)                :
                Node which is connected to all the triangles in the
                triangle set.
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
        # current node is D

        reduced_triangle_set = triangle_set.copy()
        duplicate_triangles = VirtualSet()

        for n in range(3, max(participations) + 1):
            high_part_edges = (
                edge for m, edge in enumerate(node.edge_list) if participations[m] == n
            )
            for edge in high_part_edges:
                # node            : P0 (D)
                # partner_node    : P1 (C)
                partner_node = edge.get_partner_node(node)
                # triplet_nodes : [P2, P3, P5] ([E, A, F])
                triplet_nodes = list()
                p_triangles = list()
                for triangle in reduced_triangle_set:
                    if partner_node in triangle:
                        p_triangles.append(triangle)
                        for triangle_node in triangle:
                            if triangle_node not in [node, partner_node]:
                                triplet_nodes.append(triangle_node)
                                break
                        else:
                            raise Exception(f"Corrupt triangle: {triangle}")
                # Make sure that we have P2, P3 and P5
                if len(triplet_nodes) != n:
                    continue
                # Ignore P5 (F)
                p5_node = None
                for i in range(n):
                    j, k = (i + 1) % n, (i + 2) % n
                    node1 = triplet_nodes[i]
                    node2 = triplet_nodes[j]
                    node3 = triplet_nodes[k]
                    # P5 (F) is not connected to P3, nor to P2, but
                    # P2 and P3 are connected !
                    if not (
                        E.Edge.are_connected(node1, node2)
                        or E.Edge.are_connected(node1, node3)
                    ):
                        p5_node = triplet_nodes.pop(i)  # pop P5
                        break
                else:
                    raise Exception("All nodes of 'triplet_nodes' are inter-connected!")

                # Make sure we found P5
                assert p5_node is not None
                # now that P5 has been removed from the 'triplet_nodes', it
                # is no longer a triplet.
                # We loose a bit of efficiency, while having clearer code.
                p_nodes = triplet_nodes.copy()
                del triplet_nodes
                # We have P2 and P3 left
                # The goal is to distinguish P2 and P3. P3 is connected to
                # P4 (G) and possibly other nodes, while P2 is only connected
                # to P0, P1 and P3. The P0-P1-P2 triangle must be kept, as well
                # as the P0-P2-P3 triangle.
                # But the P0-P1-P3 triangle must be removed from the
                # triangle set !
                p2_node = p3_node = None
                for p_node, alter_node in (p_nodes, reversed(p_nodes)):
                    # looking for P3
                    if len(p_node.edge_list) >= 3 and any(
                        edge.get_partner_node(p_node)
                        not in (node, partner_node, alter_node)  # (P0, P1, P(2?3))
                        for edge in p_node.edge_list
                    ):
                        p3_node = p_node
                        p2_node = alter_node
                        break
                else:
                    raise Exception(f"P2 and P3 could not be distinguished: {p_nodes}")
                # As a last step, remove the P0-P1-P3 triangle from
                # the triangle set.
                p0_p1_p3 = next(
                    triangle for triangle in p_triangles if p3_node in triangle
                )
                p0_p1_p3_set = VirtualSet([p0_p1_p3])
                reduced_triangle_set -= p0_p1_p3_set
                duplicate_triangles &= p0_p1_p3_set

        return reduced_triangle_set, duplicate_triangles
