# 3D nps & Stuff ...
from __future__ import annotations
import numpy as np, random, noise
from math import *

PI = np.pi
TWO_PI = PI * 2
HALF_PI = PI / 2
EPSILON = 10e-17

class Node:
	def __init__(self, position, connections):
		self.position = position
		self.connections = connections
		self.hidden_line = None # for hidden-line algorithm

class TriangleStrip:
	"""
	"""
	def __init__(self, width, length, offset):
		pass
def generate_triangle_strip(width, length, offset=.1):

	matrix = [[Node(None,[]) for _ in range(length+1)] for _ in range(width+1)]

	for y in range(0, width):
		for x in range(0, length):

			matrix[y][x].position = [y*offset,0,x*offset]

			matrix[y][x].connections.append(matrix[y][x+1])
			matrix[y][x].connections.append(matrix[y+1][x])

			matrix[y][x+1].connections = [matrix[y+1][x]]

	matrix = [line[:-1] for line in matrix[:-1]]

	return matrix

def clean_triangle_strip(triangle_strip):

	for line in triangle_strip:
		for node in line:
			node.connections = list(filter(lambda conn: conn.position, node.connections))


def apply_random_3D(triangle_strip):

	for line in triangle_strip:
		for node in line:
			# change node position
			node.position[1] = random.uniform(-.1,.1)

			# change node.connections position
			for conn in node.connections:
				if conn.position:
					conn.position[1] = random.uniform(-.1,.1)


def apply_perlin_3D(triangle_strip, transformation, noise_space=0):

	for line in triangle_strip:
		for node in line:
			# change node position
			x, y, z = node.position
			z += noise_space
			node.position[1] = noise.pnoise2(x, z) * transformation

			# change node.connections position
			for connection in node.connections:
				if connection.position:
					x, y, z = connection.position
					z += noise_space
					connection.position[1] = noise.pnoise2(x, z) * transformation

# vectors
class __vector__:
	def __init__(self):
		self.vector = lambda a,b: np.array([b[i]-a[i] for i in range(len(a))]) # replace 'np.array' with 'tuple' is something is broken now

		self.add = lambda vector1, vector2: [x+vector2[i] for i,x in enumerate(vector1)]
		self.subtract = lambda vector1, vector2: [x-vector2[i] for i,x in enumerate(vector1)]

		self.division = lambda vector1, vector2: [x/vector2[i] for i,x in enumerate(vector1)]
		self.division_k = lambda vector, k: [x/k for x in vector]

		self.multiplication = lambda vector1, vector2: [x*vector2[i] for i,x in enumerate(vector1)]
		self.multiplication_k = lambda vector, k: [x*k for x in vector]

		self.cross_product = lambda vector1, vector2: (vector1[1]*vector2[2] - vector1[2]*vector2[1], vector1[2]*vector2[0] - vector1[0]*vector2[2], vector1[0]*vector2[1] - vector1[1]*vector2[0])
		self.dot_product = lambda vector1, vector2: sum([vector1[i] * vector2[i] for i in range(len(vector1))])

		self.magnitude = lambda vector: np.sqrt(sum([a**2 for a in vector]))
		self.normalize = lambda vector: [x/self.magnitude(vector) for x in vector]

		self.angle = lambda vector1, vector2: np.arccos(self.dot_product(self.normalize(vector1), self.normalize(vector2)))
		self.angle_sign = lambda base_vector, vector2: 1 if vector2[0] <= base_vector[0] else -1

		self.rotate2d = lambda vector, teta: rotate2d(vector, (0,0), teta)
		self.rotate3d_x = lambda vector, teta: transformation_matrix.apply_matrix(transformation_matrix.vector_rotate3d_x_axis(teta), vector)
		self.rotate3d_y = lambda vector, teta: transformation_matrix.apply_matrix(transformation_matrix.vector_rotate3d_y_axis(teta), vector)
		self.rotate3d_z = lambda vector, teta: transformation_matrix.apply_matrix(transformation_matrix.vector_rotate3d_z_axis(teta), vector)
		self.rotate3d_vector = lambda vector1, vector2, teta: transformation_matrix.apply_matrix(transformation_matrix.vector_rotate3d_unit_vector(self.normalize(vector2)[0], self.normalize(vector2)[1], self.normalize(vector2)[2], teta), vector1)

# point 2D
class Point2D:
	def __init__(self, x, y):
		self.x = x
		self.y = y

# point 3D
class Point3D:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

# 2D plane
class Plane:
	def __init__(self, a : float, b : float, c : float, d : float):
		''' ax + by + cz + d = 0
		'''
		self.a, self.b, self.c, self.d = a, b, c, d

	def point_on_plane(self, point : list[float]) -> bool:
		return self.normal_dist(point) < EPSILON

	def normal_dist(self, point : list[float]) -> float:
		return abs(self.a*point[0] + self.b*point[1] + self.c*point[2] + self.d)

	def dist_with_point(self, point : list[float]) -> float:
		return self.normal_dist(point) / self.base()

	def base(self):
		return np.sqrt(self.a**2 + self.b**2 + self.c**2)

	@staticmethod
	def from_vectors(u : list[float], v : list[float], point : list[float] = (0,0,0)) -> Plane:
		'''Get the Plane defined with the two given vectors, starting from the 'point'
		'''
		normal = np.cross(u, v)
		a, b, c = normal
		d = -(a*point[0] + b*point[1] + c*point[2])
		return Plane(a, b, c, d)

	@staticmethod
	def from_points(P : list[float], Q : list[float], R : list[float]) -> Plane:
		'''Get the Plane that passes through those 3 points
		'''
		PQ = vector.vector(P, Q)
		PR = vector.vector(P, R)
		return Plane.from_vectors(PQ, PR, P)


# transformation matrices
class __transformation_matrix__:
	def __init__(self):
		self.vector_rotate2d = lambda teta: [[np.cos(teta), -np.sin(teta)],[np.sin(teta), np.cos(teta)]]
		self.vector_rotate3d_x_axis = lambda teta: [[1,0,0],[0,np.cos(teta),-np.sin(teta)],[0,np.sin(teta),np.cos(teta)]]
		self.vector_rotate3d_y_axis = lambda teta: [[np.cos(teta),0,np.sin(teta)],[0,1,0],[-np.sin(teta),0,np.cos(teta)]]
		self.vector_rotate3d_z_axis = lambda teta: [[np.cos(teta),-np.sin(teta),0],[np.sin(teta),np.cos(teta),0],[0,0,1]]
		self.vector_rotate3d_unit_vector = lambda teta, ux, uy, uz: [[(1 - np.cos(teta))*ux**2 + np.cos(teta), (1 - np.cos(teta))*ux*uy - np.sin(teta)*uz, (1 - np.cos(teta))*ux*uz + np.sin(teta)*uy],
																	 [(1 - np.cos(teta))*ux*uy + np.sin(teta)*uz, (1 - np.cos(teta))*uy**2 + np.cos(teta), (1 - np.cos(teta))*uy*uz - np.sin(teta)*ux],
																	 [(1 - np.cos(teta))*ux*uz - np.sin(teta)*uy, (1 - np.cos(teta))*uy*uz + np.sin(teta)*ux, (1 - np.cos(teta))*uz**2 + np.cos(teta)]]
		self.apply_matrix = lambda matrix, vector: [sum([matrix[a][b]*vector[b] for b in range(len(vector))]) for a in range(len(matrix))]

transformation_matrix = __transformation_matrix__()
vector = __vector__()

# euclidean distance
distance2d = lambda a, b: np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
distance3d = lambda a, b: np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2 + (b[2] - a[2])**2)
distance = lambda a, b: np.sqrt(sum( [ (b[i] - a[i]) ** 2 for i in range(len(a)) ] ))
distance1 = lambda t: ditance(t[0], t[1]) # 1 variable
distance_point_to_plane = lambda point, a, b, c, d = 0: abs(a*point[0] + b*point[1] + c*point[2] + d) / np.sqrt(a**2 + b**2 + c**2) # point = (x1, y1, z1) & plane = ax + by + cz + d

# simple rotate
rotate2d = lambda a, b, teta: (np.cos(teta) * (a[0] - b[0]) - np.sin(teta) * (a[1] - b[1]) + b[0], np.sin(teta) * (a[0] - b[0]) + np.cos(teta) * (a[1] - b[1]) + b[1])

# straight lines
slope = lambda a, b: (b[1] - a[1]) / (b[0] - a[0])
line_equation = lambda a,b: lambda x: slope(a,b) * (x - a[0]) + a[1]
intersection = lambda x1,y1,x2,y2,x3,y3,x4,y4: [( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) ), ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )]

# surface of a triangle by coordinates or vectors
triangle_surface2d = lambda a,b,c : abs(a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1])) / 2
triangle_surface2d_vect = lambda ab,ac: triangle_surface2d((0,0),ab,ac)
triangle_surface3d = lambda a,b,c: triangle_surface3d_vect(vector.vector(a,b),vector.vector(a,c))
triangle_surface3d_vect = lambda ab,ac : np.sqrt((ab[1]*ac[2] - ab[2]*ac[1])**2 + (ab[2]*ac[0] - ab[0]*ac[2])**2 + (ab[0]*ac[1] - ab[1]*ac[0])**2) / 2

# angles
deg_to_rad = lambda a: a * np.pi/180
rad_to_deg = lambda a: a * 180/np.pi

# triangles
centroid_of_triangle = lambda a, b, c: [(a[i] + b[i] + c[i]) / 3 for i in range(len(a))] # shoud work with any dim (except dim = -inf ?)

def get_x_axis_surface(triangle_strip):
	# This is all as in 2D np. Consider it as a plane projected on a 3D space

	depth = len(triangle_strip[0])

	# create max_y and min_y: they store the max and min depth per column
	max_y = [(-1.1,0) for _ in range(depth)]
	min_y = [(np.inf,0) for _ in range(depth)]

	# retrieve those values
	for line in triangle_strip:
		for x,node in enumerate(line):

			# z too, because the elasticity can change it
			if node.position[1] > max_y[x][0]:
				max_y[x] = node.position[1:]
			if node.position[1] < min_y[x][0]:
				min_y[x] = node.position[1:]

	# the center of this irregular is defined (musn't be the real center) by approximatively it's middle
	middle_index = depth // 2
	center_of_polygon = (min_y[middle_index][0]+(max_y[middle_index][0] - min_y[middle_index][0]) / 2, max_y[middle_index][1])

	# will be a list of 3 coordinates-tuple
	triangles = []

	# create all triangles
	for i in range(depth-1):

		triangles.append([max_y[i], max_y[i+1], center_of_polygon])
		triangles.append([min_y[i], min_y[i+1], center_of_polygon])

	# sum up the surfaces of all those triangles
	surface = sum([triangle_surface2d(triangle[0], triangle[1], triangle[2]) for triangle in triangles])

	return surface


def get_z_axis_surface(triangle_strip):
	# This is all as in 2D np. Consider it as a plan projected on a 3D space

	length = len(triangle_strip)

	# create max_y and min_y: they store the max and min length per row
	max_y, min_y = [], []

	# retrieve those values
	for line in triangle_strip:
		# x too, because the elasticity can change it
		max_y.append(max([coord.position[:2] for coord in line], key=lambda x: x[1])[::-1])
		min_y.append(min([coord.position[:2] for coord in line], key=lambda x: x[1])[::-1])

	# the center of this irregular is defined (musn't be the real center) by approximatively it's middle
	middle_index = length // 2
	center_of_polygon = (min_y[middle_index][0]+(max_y[middle_index][0] - min_y[middle_index][0]) / 2, max_y[middle_index][1])

	# will be a list of 3 coordinates-tuple
	triangles = []

	# create all triangles
	for i in range(length-1):

		triangles.append([max_y[i], max_y[i+1], center_of_polygon])
		triangles.append([min_y[i], min_y[i+1], center_of_polygon])

	# sum up the surfaces of all those triangles
	surface = sum([triangle_surface2d(triangle[0], triangle[1], triangle[2]) for triangle in triangles])

	return surface

def no_x_before(node_index, triangle_strip, sign): # sign: 1 => begin to end, 2 => end to begin

	x, y, z = triangle_strip[node_index[0]][node_index[1]].position

	for line in triangle_strip[:node_index[0]:sign]:
		# get the two closest nodes (should? be right and left of the node)s
		node1, node2 = sorted(line, key=lambda node: abs(z - node.position[2]))[:2]

		x1, y1, z1 = node1.position
		x2, y2, z2 = node2.position

		slope = (y2 - y1) / (z2 - z1)
		# y - y1 = m(x - x1)

		# remember it's a 2d plan projected on a 3d space, so plane np is authorized ;-)
		equation = lambda dz: (slope * (dz - z1) + y1) * sign

		if equation(z) >= y: # > or >= ? : think about > and a totally flat sheet
			return False

	return True

def no_z_before(node_index, triangle_strip, sign): # sign: 1 => begin to end, 2 => end to begin

	x, y, z = triangle_strip[node_index[0]][node_index[1]].position

	for line in list(zip(*triangle_strip))[:node_index[1]:sign]:
		# get the two closest nodes (should? be right and left of the node)s
		node1, node2 = sorted(line, key=lambda node: abs(x - node.position[0]))[:2]

		x1, y1, z1 = node1.position
		x2, y2, z2 = node2.position

		slope = (y2 - y1) / (x2 - x1)
		# y - y1 = m(x - x1)

		# remember it's a 2d plan projected on a 3d space, so plane np is authorized ;-)
		equation = lambda dx: (slope * (dx - x1) + y1) * sign

		if equation(x) >= y:
			return False

	return True

def reverse_triangle_strip(triangle_strip):

	for line in triangle_strip:
		for node in line:
			node.position[1] *= -1


def hidden_line_algorithm_x_axis(triangle_strip, sign):

	nodes = []

	# select all nodes in sight (from x and sign)
	for y,line in enumerate(triangle_strip): # the first two are too problematic for
		for x,node in enumerate(line):
			if no_x_before((y,x), triangle_strip, sign):
				nodes.append(node)
				node.hidden_line = 'top'

	# reverse the whole triangle_strip (in y axis) for the 1st time
	reverse_triangle_strip(triangle_strip)

	# select all nodes in sight (from x and sign)
	for y,line in enumerate(triangle_strip):
		for x,node in enumerate(line):
			if no_x_before((y,x), triangle_strip, sign):
				nodes.append(node)
				node.hidden_line = 'bottom'

	# reverse the whole triangle_strip (in y axis) for the 2nd time
	reverse_triangle_strip(triangle_strip)

	return nodes

def hidden_line_algorithm_z_axis(triangle_strip, sign):

	nodes = []

	# select all nodes in sight (from x and sign)
	for y,line in enumerate(triangle_strip):
		for x,node in enumerate(line):
			if no_z_before((y,x), triangle_strip, sign):
				nodes.append(node)
				node.hidden_line = 'top'

	# reverse the whole triangle_strip (in y axis) for the 1st time
	reverse_triangle_strip(triangle_strip)

	# select all nodes in sight (from x and sign)
	for y,line in enumerate(triangle_strip):
		for x,node in enumerate(line):
			if no_z_before((y,x), triangle_strip, sign):
				nodes.append(node)
				node.hidden_line = 'bottom'

	# reverse the whole triangle_strip (in y axis) for the 2nd time
	reverse_triangle_strip(triangle_strip)

	return nodes

def triangle_strip_dist_per_node(triangle_strip, diagonal=False, return_sum=False):

	distances = []

	for line in triangle_strip[:-1]:
		for node in line[:-1]:

			'''

			 A -------- B
			 |
			 |
			 |
			 |
			 C

			'''

			A = node.position
			B, C = [c.position for c in node.connections[:2]]

			AB, AC = distance3d(A,B), distance3d(A,C)

			if diagonal: distances.append(sum([AB, AC, distance3d(B,C)]))
			else: distances.append(AB + AC)

	for node in triangle_strip[-1][:-1]:

		distances.append(distance3d(node.position, node.connections[0].position))

	for node in [line[-1] for line in triangle_strip[:-1]]:

		distances.append(distance3d(node.position, node.connections[0].position))

	if return_sum: return sum(distances)
	else: return distances

# a little bit more complicated nps stuff comes here

# Chaikin Polynom smoothing Algorithm
def Chaikin(nodes : list[tuple[float]], *args) -> list:
	n : int = args[0] if args else 6
	n_m : int = n - 1
	new_nodes : list = []

	for i in range(-1, len(nodes)-1):
		p_p1_vector : list = matrix.vector.vector(nodes[i], nodes[i+1])
		q : list = matrix.vector.multiplication_k(p_p1_vector, 1 / n)
		r : list = matrix.vector.multiplication_k(p_p1_vector, n_m / n)
		q : list = matrix.vector.add(nodes[i], q)
		r : list = matrix.vector.add(nodes[i], r)
		new_nodes.append(q)
		new_nodes.append(r)

	return new_nodes

def polynomial_function_coefficients_from_3_points(x1, y1, x2, y2, x3, y3):
	a = (x1 * (y3 - y2) + x2 * (y1 - y3) + x3 * (y2 - y1)) / \
		((x1 - x2) * (x1 - x3) * (x2 - x3))
	b = (y2 - y1)/(x2 - x1) - a * (x1 + x2)
	c = y1 - a*x1**2 - b*x1
	return a, b, c































def debug_triangle_strip(triangle_strip):

	try: triangle_strip[0]
	except TypeError: raise TypeError('the triangle_strip is not a strip anymore. It\'s type is {}'.format(type(triangle_strip)))

	try: triangle_strip[0][0]
	except TypeError: raise TypeError('the triangle_strip\' is not are not lines anymore. Their type is {}'.format(type(triangle_strip[0])))

	assert all([type(node) == Node for node in [line for line in triangle_strip]])
	assert all([hasattr(node, 'position') for node in [line for line in triangle_strip]])
	assert all([hasattr(node, 'connections') for node in [line for line in triangle_strip]])

	for line in triangle_strip:
		for node in line:

			assert len(node.position) == 3
			assert all([type(x) == float for x in node.position])

			assert 1 <= len(node.connections) <= 3

			assert all([connection != None for connection in node.connections])
