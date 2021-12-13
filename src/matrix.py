from __future__ import annotations
import numpy as np

EPSILON = 10e-17


def vector_from_points(u: np.array, v: np.array) -> np.array:
    """
    Return the vector 'uv', from points 'u' to 'v'.

    Args:
        u (np.array): Point 'u'.
        v (np.array): Point 'v'.

    Returns:
        np.array: vector

    """

    return v - u


# 2D plane
class Plane:
    """
    2D Plane class.

    """

    def __init__(self, a: float, b: float, c: float, d: float):
        """ax + by + cz + d = 0"""
        self.a, self.b, self.c, self.d = a, b, c, d

    def point_on_plane(self, point: np.array) -> bool:
        """
        Is the given point on this plane ?

        If the distance to th eplane is less than EPSILON, the point is
        considered to be on the plane.

        Args:
            point (np.array): Point to check.

        Returns:
            bool: The point is one the plane.

        """

        return self.normal_dist(point) < EPSILON

    def normal_dist(self, point: np.array) -> float:
        """
        Return the normal distance of the 'point' to the plane.

        Args:
            point (np.array): Point to check.

        Returns:
            float: Normal distance to the plane.

        """

        return abs(self.a * point[0] + self.b * point[1] + self.c * point[2] + self.d)

    def dist_with_point(self, point: np.array) -> float:
        """
        Return the distance of the 'point' to the plane.

        Args:
            point (np.array): Point to check.

        Returns:
            float: Distance to the plane.

        """

        return self.normal_dist(point) / self.base()

    def base(self):
        """
        Return the base of the plane.

        Returns:
            float: The base of the plane.

        """

        return np.sqrt(self.a ** 2 + self.b ** 2 + self.c ** 2)

    @staticmethod
    def from_vectors(u: np.array, v: np.array, point: np.array = (0, 0, 0)) -> Plane:
        """
        Returns the Plane defined with the two given vectors, starting from the 'point'.

        Args:
            u     (np.array): Vector u.
            v     (np.array): Vector v.
            point (np.array): Starting point.

        Returns:
            Plane: Plane defined by the triplet (point, u(vect), v(vect)).

        """

        normal = np.cross(u, v)
        a, b, c = normal
        d = -(a * point[0] + b * point[1] + c * point[2])
        return Plane(a, b, c, d)

    @staticmethod
    def from_points(P: np.array, Q: np.array, R: np.array) -> Plane:
        """
        Returns the Plane defined by those 3 points.

        Returns the Plane defined by (P, PQ(vect), PR(vect))

        Args:
            P (np.array): First point.
            Q (np.array): Second point.
            R (np.array): Third point.

        Returns:
            Plane: Plane defined by those 3 points.

        """

        PQ = vector.vector(P, Q)
        PR = vector.vector(P, R)
        return Plane.from_vectors(PQ, PR, P)
