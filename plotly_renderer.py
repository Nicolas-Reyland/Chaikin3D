# Polygon rendering
import plotly.graph_objects as go
from polygon import Polygon

DO_CHAIKIN = True

def gen_random_color():
	s = '#'
	import random
	choices = '0123456789abcdef'
	for _ in range(6):
		s += random.choice(choices)
	return s

class Renderer:
	def __init__(self):
		pass

	def draw_polygon(self, polygon : Polygon, alpha : float = 0.8, draw_text : bool = True):
		figure_data : list[go.Mesh3d] = []
		X, Y, Z = [], [], []
		I, J, K = [], [], []
		vertex_list = []
		vertex_index_list = []
		for triplet in polygon:
			index_list = []
			for vertex in triplet:
				if vertex not in vertex_list:
					vertex_list.append(vertex)
					index_list.append(len(vertex_list) - 1)
				else:
					index_list.append(vertex_list.index(vertex))
			vertex_index_list.append(index_list)

		X, Y, Z = list(zip(*vertex_list))
		I, J, K = list(zip(*vertex_index_list))

		fig = go.Figure(data=[go.Mesh3d(
			x=X, y=Y, z=Z,
			#color=gen_random_color(),
			i=I,
			j=J,
			k=K,
			opacity=alpha
		)])
		fig.show()

