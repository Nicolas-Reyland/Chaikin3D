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
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs

	def draw(self, data : list):
		fig = go.Figure(data, *self.args, **self.kwargs)
		fig.show()

	def get_polygon_draw_data(self, polygon : Polygon, alpha : float = 0.8, draw_text : bool = True, color : str = 'lightblue') -> list[go.Mesh3d]:
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
		return [go.Mesh3d(
			x=X, y=Y, z=Z,
			color=gen_random_color() if color == 'random' else color,
			i=I,
			j=J,
			k=K,
			opacity=alpha
		)]

	def draw_polygon(self, polygon : Polygon, alpha : float = 0.8, draw_text : bool = True) -> None:
		self.draw(data=self.get_polygon_draw_data(polygon, alpha, draw_text))

	def get_connections_draw_data(self, polygon : Polygon, type_ : str = 'any', color : str = 'lightblue', width : int = 2) -> list[go.Scatter3d]:
		figure_data : list[go.Scatter3d] = []
		for connection in polygon.get_connections(type_):
			A, B = connection.A.coords, connection.B.coords
			figure_data.append(go.Scatter3d(
				x = [A[0], B[0]],
				y = [A[1], B[1]],
				z = [A[2], B[2]],
				line={
					'color': gen_random_color() if color == 'random' else color,
					'width': width
				}
			))
		return figure_data

	def draw_connections(self, polygon : Polygon, type_ : str = 'any', color : str = 'lightblue', width : int = 2) -> None:
		self.draw(data=self.get_connections_draw_data(polygon, type_, color, width))


'''
fig = go.Figure(
	data=[
		go.Scatter3d(
			x = [0,1,2],
			y = [0,2,1],
			z = [1,1,1],
			line=dict(
				color='darkblue',
				width=2
			)
		),
		go.Scatter3d(
			x = [2,1,2],
			y = [2,1,0],
			z = [0,2,0],
			line=dict(
				color='darkblue',
				width=2
			)
		)
	]
)


fig.show()
'''
