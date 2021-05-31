#
import math
import basic_shapes

RENDERER = 'plotly' # 'mpl'

if RENDERER == 'plotly':
	from plotly_renderer import *
elif RENDERER == 'mpl':
	from mpl_renderer import *
else:
	raise Exception('Unkown renderer:', RENDERER)

def draw_full(renderer : Renderer, poly : Polygon) -> None:
	main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', color = 'darkred')
	graphical_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'graphical', color = 'black')
	main_poly_dd = renderer.get_polygon_draw_data(poly, type_ = 'main', alpha = .6, color = 'lightblue')
	graphical_poly_dd = renderer.get_polygon_draw_data(poly, type_ = 'graphical', alpha = .6, color = 'lightblue')
	alpha_poly_dd = renderer.get_polygon_draw_data(poly, alpha = .6, color = 'lightblue')
	poly_dd = renderer.get_polygon_draw_data(poly, alpha = 1, color = 'lightblue')
	all_connection_dd = graphical_conn_dd + main_conn_dd

	print(' - drawing -')
	renderer.init_subplots(3, 3)

	# add from least important to most important (adding the lists of data, not subplot order) -> visual overwriting
	for sub_mpoly_dd in main_poly_dd:
		renderer.add_to_subplot(sub_mpoly_dd, custom_row = 2, custom_col = 1)
	for sub_gpoly_dd in graphical_poly_dd:
		renderer.add_to_subplot(sub_gpoly_dd, custom_row = 2, custom_col = 2)
	for sub_poly_dd in poly_dd:
		renderer.add_to_subplot(sub_poly_dd, custom_row = 2, custom_col = 3)
	for sub_apoly_dd in alpha_poly_dd:
		renderer.add_to_subplot(sub_apoly_dd, custom_row = 3, custom_col = 1)
		renderer.add_to_subplot(sub_apoly_dd, custom_row = 3, custom_col = 2)
		renderer.add_to_subplot(sub_apoly_dd, custom_row = 3, custom_col = 3)
	for gconn_dd in graphical_conn_dd:
		renderer.add_to_subplot(gconn_dd, custom_row = 1, custom_col = 3)
		renderer.add_to_subplot(gconn_dd, custom_row = 1, custom_col = 2)
		renderer.add_to_subplot(gconn_dd, custom_row = 3, custom_col = 3)
		renderer.add_to_subplot(gconn_dd, custom_row = 2, custom_col = 2)
	for mconn_dd in main_conn_dd:
		renderer.add_to_subplot(mconn_dd, custom_row = 1, custom_col = 1)
		renderer.add_to_subplot(mconn_dd, custom_row = 1, custom_col = 3)
		renderer.add_to_subplot(mconn_dd, custom_row = 3, custom_col = 2)
		renderer.add_to_subplot(mconn_dd, custom_row = 3, custom_col = 3)
		renderer.add_to_subplot(mconn_dd, custom_row = 2, custom_col = 1)

	renderer.draw_subplots()

def draw_chaikin_evolution(renderer : Renderer, poly : Polygon, n : int) -> None:
	# find best row-col combination
	assert n > 0
	near = math.sqrt(n)
	rows = int(near) + (0 if near == int(near) else 1)
	cols = rows
	renderer.init_subplots(rows, cols, subplot_titles=['Chaikin Gen {}'.format(i) for i in range(n)])
	for i in range(n):
		print('Generation: {}'.format(i))
		alpha_poly_dd = renderer.get_polygon_draw_data(poly, alpha = .6, color = 'lightblue')
		main_conn_dd = main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', color = 'darkred')
		for sub_apoly_dd in alpha_poly_dd:
			renderer.add_to_subplot(sub_apoly_dd)
		for mconn_dd in main_conn_dd:
			renderer.add_to_subplot(mconn_dd)
		renderer.next_subplot()
		# Chaikin
		poly = Polygon.Chaikin3D(poly, 4)

	renderer.draw_subplots()

def chaikin_animation(renderer : Renderer, poly : Polygon, n : int) -> None:
	frames : list[go.Frame] = []
	old_poly = Polygon(poly.nodes.copy())
	for gen in range(n):
		alpha_poly_dd = renderer.get_polygon_draw_data(poly, alpha = .6, color = 'lightblue')
		main_conn_dd = main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', color = 'darkred')
		frames.append(go.Frame(
			data=alpha_poly_dd + main_conn_dd,
			name='Chaikin Gen {}'.format(gen)
		))
		if gen < n: poly = Polygon.Chaikin3D(poly)
	fig = go.Figure(frames=frames)
	# add first frame
	alpha_poly_dd = renderer.get_polygon_draw_data(poly, alpha = .6, color = 'lightblue')
	main_conn_dd = main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', color = 'darkred')
	fig.add_trace(alpha_poly_dd + main_conn_dd)
	#
	frame_args = lambda duration: 	{
										"frame": {"duration": duration},
										"mode": "immediate",
										"fromcurrent": True,
										"transition": {"duration": duration, "easing": "linear"},
									}
	#
	sliders = [
			{
				"pad": {"b": 10, "t": 60},
				"len": 0.9,
				"x": 0.1,
				"y": 0,
				"steps": [
					{
						"args": [[f.name], frame_args(0)],
						"label": str(k),
						"method": "animate",
					}
					for k, f in enumerate(fig.frames)
				],
			}
		]
	# Layout
	fig.update_layout(
			 title='Chaikin Algorithm in 3 dimensions',
			 width=600,
			 height=600,
			 updatemenus = [
				{
					"buttons": [
						{
							"args": [None, frame_args(50)],
							"label": "&#9654;", # play symbol
							"method": "animate",
						},
						{
							"args": [[None], frame_args(0)],
							"label": "&#9724;", # pause symbol
							"method": "animate",
						},
					],
					"direction": "left",
					"pad": {"r": 10, "t": 70},
					"type": "buttons",
					"x": 0.1,
					"y": 0,
				}
			 ],
			 sliders=sliders
	)

	fig.show()



def main():
	global DO_CHAIKIN
	renderer = Renderer()
	poly = basic_shapes.cube()
	#poly = basic_shapes.triangle()

	DO_CHAIKIN = 0

	if DO_CHAIKIN:
		for _ in range(1):
			print(' - 3D Chaikin -')
			poly = Polygon.Chaikin3D(poly, 4)
	#renderer.draw_polygon(poly, alpha = 1, draw_text = False)

	#draw_full(renderer, poly)
	draw_chaikin_evolution(renderer, poly, 5)
	print('done')

	#figure_data = graphical_conn_dd + main_conn_dd + poly_dd
	#renderer.draw(figure_data)

	return poly

if __name__ == '__main__':
	main()

