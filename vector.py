#
import numpy as np
import matrix

class Vector3D:
	def __init__(self, coords : tuple[float]):
		self.x, self.y, self.z = coords
		self.coords = coords if type(coords) == np.ndarray else np.array(coords)

	def normalize(self):
		mag = self.magnitude()
		return Vector3D((
			self.x / mag,
			self.y / mag,
			self.z / mag
		))
		
	def magnitude(self):
		return matrix.vector.magnitude(self.coords)

	def spherical_coordinates(self):
		'''return-values: (r, teta, phi)
		r : magnitude
		teta: x-y rad (x as base axes)
		phi: z rad
		'''
		r = self.magnitude()
		teta = np.arctan(self.coords[1] / self.coords[0]) if self.coords[0] != 0 else matrix.HALF_PI
		phi = np.arctan(np.sqrt(self.coords[0]**2 + self.coords[1]**2) / self.coords[2]) if self.coords[2] != 0 else 0

		return r, teta, phi

