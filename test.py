#
import matrix
import numpy as np
from renderer import Renderer, Polygon
from vector import Vector3D

def reduce_circle_to_polygon(center : list[float], normal_vector : Vector3D, radius : float, num_points : int, rad_offset : float = 0) -> Polygon:
	# calculate the points in the 2D plane
	points_in_plane = []
	rad_step = matrix.TWO_PI / num_points
	rad = rad_offset
	full_circle = matrix.TWO_PI + rad_offset
	while rad < full_circle:
		#
		point_x = np.sin(rad) * radius
		point_y = np.cos(rad) * radius
		#
		points_in_plane.append((point_x, point_y))
		rad += rad_step
	# project the points into the 3D space
	normal_vector = normal_vector.normalize() # if not normalized yet
	_, teta, phi = normal_vector.spherical_coordinates()
	points_in_space = []
	rotation_matrix = np.array(matrix.transformation_matrix.vector_rotate3d_unit_vector(matrix.HALF_PI, normal_vector.x, normal_vector.y, normal_vector.z))
	count = 0
	for (x,y) in points_in_plane:
		point = np.array([x, y, 0])
		# rotate
		point = np.matmul(rotation_matrix, point)
		point = matrix.vector.add(center, point)
		# translate
		points_in_space.append(point)
		# re-add center to make up triangles
		count += 1
		if count == 2:
			points_in_space.append(center)
			count = 0

	return Polygon.from_raw_points(points_in_space)

polygon = reduce_circle_to_polygon(
	[.5,.5,.5],			# center
	Vector3D((1,1,0)),	# normal-vector
	0.5,				# radius
	8,					# num_points
	0					# rad_offset
)

renderer = Renderer()
renderer.draw_polygon(polygon)

#
