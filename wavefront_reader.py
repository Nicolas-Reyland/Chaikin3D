#
from __future__ import annotations
from polygon import Polygon
import os

class ObjMesh:
	def __init__(self, path : str):
		# attributes
		self.path : str = os.path.abspath(path)
		assert os.path.isfile(self.path)
		self.vertices : list[list[float]] = []
		self.vertex_indices : list[list[int]] = []
		self.parse()
		# lambdas
		self.to_polygon = lambda : Polygon.from_standard_vertex_lists(self.vertices, self.vertex_indices)

	def parse(self):
		lines = open(self.path, 'r').readlines()
		vertices_str = []
		vertex_indices_str = []
		for line in lines:
			# vertex line
			if line.startswith('v '):
				vertices_str.append(line[2:])
			elif line.startswith('f '):
				vertex_indices_str.append(line[2:])

		print('obj file -> num vertices:', len(vertices_str))
		print('obj file -> num connections:', len(vertex_indices_str))

		for vertex_str in vertices_str:
			raw_vert = list(filter(None, vertex_str.split()))
			raw_vert = raw_vert[:3]
			#assert len(raw_vert) == 3 # could be 4 bc of w ( = 1.0)
			self.vertices.append(list(map(float, raw_vert)))

		for vertex_index_str in vertex_indices_str:
			raw_vert_index = list(filter(None, vertex_index_str.split()))
			raw_vert_index = raw_vert_index[:3]
			#assert len(raw_vert_index) == 3
			vertex_index = []
			for raw_sub_vertex_index in raw_vert_index:
				index = int(raw_sub_vertex_index.split('/')[0])
				vertex_index.append(index)
			self.vertex_indices.append(vertex_index)

