#
import basic_shapes

RENDERER = 'plotly' # 'mpl'

if RENDERER == 'plotly':
	from plotly_renderer import *
elif RENDERER == 'mpl':
	from mpl_renderer import *
else:
	raise Exception('Unkown renderer:', RENDERER)

def main():
	global DO_CHAIKIN
	renderer = Renderer()
	#poly = basic_shapes.cube()
	poly = basic_shapes.triangle()

	DO_CHAIKIN = 1

	if DO_CHAIKIN:
		for _ in range(1):
			print(' - 3D Chaikin -')
			poly = Polygon.Chaikin3D(poly, 4)

	print(' - drawing -')
	#renderer.draw_polygon(poly, alpha = 1, draw_text = False)

	figure_data = []
	figure_data.extend(renderer.get_connections_draw_data(poly, type_ = 'graphical', color = 'black'))
	figure_data.extend(renderer.get_connections_draw_data(poly, type_ = 'main', color = 'darkred'))
	figure_data.extend(renderer.get_polygon_draw_data(poly, alpha = .6, color = 'lightblue'))
	renderer.draw(figure_data)

	return poly

if __name__ == '__main__':
	main()

