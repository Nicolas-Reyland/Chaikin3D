from __future__ import annotations
import numpy as np

EPSILON = 10e-17


def vector_from_points(u: np.array, v: np.array) -> np.array:
    return v - u


# 2D plane
class Plane:
    def __init__(self, a: float, b: float, c: float, d: float):
        """ax + by + cz + d = 0"""
        self.a, self.b, self.c, self.d = a, b, c, d

    def point_on_plane(self, point: list[float]) -> bool:
        return self.normal_dist(point) < EPSILON

    def normal_dist(self, point: list[float]) -> float:
        return abs(self.a * point[0] + self.b * point[1] + self.c * point[2] + self.d)

    def dist_with_point(self, point: list[float]) -> float:
        return self.normal_dist(point) / self.base()

    def base(self):
        return np.sqrt(self.a ** 2 + self.b ** 2 + self.c ** 2)

    @staticmethod
    def from_vectors(
        u: list[float], v: list[float], point: list[float] = (0, 0, 0)
    ) -> Plane:
        """Get the Plane defined with the two given vectors, starting from the 'point'"""
        normal = np.cross(u, v)
        a, b, c = normal
        d = -(a * point[0] + b * point[1] + c * point[2])
        return Plane(a, b, c, d)

    @staticmethod
    def from_points(P: list[float], Q: list[float], R: list[float]) -> Plane:
        """Get the Plane that passes through those 3 points"""
        PQ = vector.vector(P, Q)
        PR = vector.vector(P, R)
        return Plane.from_vectors(PQ, PR, P)
