#!/usr/bin/env python3
from math import sqrt
from polyhedron import Polyhedron
from wavefront_reader import WaveFrontReader

from argparse import ArgumentParser
parser = ArgumentParser(description='Apply the Chaikin algorithm, expanded for the 3D space')

# polyhedron
parser.add_argument('-i', '--input', type=str, help='input file (df. None)')
parser.add_argument('-e', '--evaluate', type=str, help='python str to evaluate right after the loading phase (df. "")')
parser.add_argument('-rm', '--rotate-mesh', type=str, help='Rotate the mesh when loading a file (df. false)')
# chaikin algorithm
parser.add_argument('-cg', '--chaikin-generations', type=int, help='number of chaikin generations (df. 0)')
parser.add_argument('-cc', '--chaikin-coef', type=float, help='Chaikin coefficient (df. 4)')
parser.add_argument('-v', '--verbose', type=str, help='verbose (boolean) (df. false)')
# what to plot
parser.add_argument('-r', '--renderer', type=str, help='renderer ["plotly", "mpl"] (df. plotly)')
parser.add_argument('-p', '--plot', type=str, help='plot type ["simple", "full", "evolution", "animation"] (df. simple)')
parser.add_argument('-smc', '--show-main-connections', type=str, help='Show the main connections (for plots: "simple", "full" and "evolution") (df. true)')
parser.add_argument('-sgc', '--show-graphical-connections', type=str, help='Show the graphical connections (for plots: "simple", "full" and "evolution") (df. false)')
# how to plot
parser.add_argument('-a', '--alpha', type=float, help='Alpha/Opacity value for mesh rendering (df. 0.8)')
parser.add_argument('-pc', '--polygon-color', type=str, help='Polygon color (df. "lightblue")')
parser.add_argument('-nc', '--node-color', type=str, help='Node color (df. "green")')
parser.add_argument('-mcc', '--main-connection-color', type=str, help='Main connection color (df. "darkred")')
parser.add_argument('-gcc', '--graphical-connection-color', type=str, help='Graphical connection (df. "black")')
# other
parser.add_argument('-t', '--test', type=str, help='Only used with \'-i\'. The input file should be tested for many attributes (df. false)')

# parse the command line arguments
args = vars(parser.parse_args())

def parse_bool(s):
	if s.lower() in ['1', 't', 'true']: return True
	if s.lower() in ['0', 'f', 'false']: return False
	raise Exception('Unrecognized value for supposed boolean:', s)

# Arguments

# polyhedron
input_file = args['input']
evaluation_string = args['evaluate'] if args['evaluate'] else ''
rotate_mesh = parse_bool(args['rotate_mesh']) if args['rotate_mesh'] else False
# chaikin
chaikin_gens = args['chaikin_generations'] if args['chaikin_generations'] else 0
verbose = parse_bool(args['verbose']) if args['verbose'] else False
chaikin_coef = args['chaikin_coef'] if args['chaikin_coef'] else 4
# what to plot
RENDERER = args['renderer'] if args['renderer'] else 'plotly'
plot = args['plot'] if args['plot'] else 'simple'
smc = parse_bool(args['show_main_connections']) if args['show_main_connections'] else True
sgc = parse_bool(args['show_graphical_connections']) if args['show_graphical_connections'] else False
# how to plot
alpha = args['alpha'] if args['alpha'] else .8
polygon_color = args['polygon_color'] if args['polygon_color'] else 'lightblue'
node_color = args['node_color'] if args['node_color'] else 'green'
main_conn_color = args['main_connection_color'] if args['main_connection_color'] else 'darkred'
graph_conn_color = args['graphical_connection_color'] if args['graphical_connection_color'] else 'black'
# other
test = args['test'] if args['test'] else False


# Test Mode
if test:
	invalid_option = [
		''
	]
	for invalid_option in invalid_options:
		if args[invalid_option] is not None:
			raise Exception('Cannot use this option with \'-t\'/\'--test\': {}'.format(invalid_option))




if RENDERER == 'plotly':
	from plotly_renderer import *
elif RENDERER == 'mpl':
	from mpl_renderer import *
else:
	raise Exception('Unkown renderer:', RENDERER)

# functions
def draw_full(renderer : Renderer, poly : Polyhedron) -> None:
	main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', line_color = main_conn_color, node_color = node_color)
	graphical_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'graphical', line_color = graph_conn_color, node_color = node_color)
	main_poly_dd = renderer.get_polyhedron_draw_data(poly, type_ = 'main', alpha = .6, color = polygon_color)
	graphical_poly_dd = renderer.get_polyhedron_draw_data(poly, type_ = 'graphical', alpha = .6, color = polygon_color)
	alpha_poly_dd = renderer.get_polyhedron_draw_data(poly, alpha = .6, color = polygon_color)
	poly_dd = renderer.get_polyhedron_draw_data(poly, alpha = 1, color = polygon_color)
	all_connection_dd = graphical_conn_dd + main_conn_dd

	renderer.init_subplots(3, 3, subplot_titles=[
		'Main connections',
		'Graphical connections',
		'All connections',
		'Faces using main connections',
		'Faces using graphical connections',
		'All faces (solid)',
		'All faces',
		'All faces + main connections',
		'All faces + all connections'
		]
	)

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

def draw_chaikin_evolution(renderer : Renderer, poly : Polyhedron, n : int, coef : float, alpha : float = .8) -> None:
	# find best row-col combination
	assert n > 0
	near = sqrt(n + 1)
	cols = int(near) + (0 if near == int(near) else 1)
	rows = cols if cols ** (cols - 1) <= n else cols - 1
	print('cols', cols, 'rows', rows)
	renderer.init_subplots(rows, cols, subplot_titles=['Chaikin Gen {}'.format(i) for i in range(n + 1)])
	for i in range(n + 1):
		print('Generation: {}'.format(i))
		# get values
		alpha_poly_dd = renderer.get_polyhedron_draw_data(poly, alpha = alpha, color = polygon_color)
		if smc: main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', line_color = main_conn_color, node_color = node_color)
		if sgc: graphical_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'graphical', line_color = graph_conn_color, node_color = node_color)
		# add to subplot
		for sub_apoly_dd in alpha_poly_dd:
			renderer.add_to_subplot(sub_apoly_dd)
		if smc:
			for mconn_dd in main_conn_dd:
				renderer.add_to_subplot(mconn_dd)
		if sgc:
			for gconn_dd in graphical_conn_dd:
				renderer.add_to_subplot(gconn_dd)
		# go to next plot
		renderer.next_subplot()
		# Chaikin
		poly = Polyhedron.Chaikin3D(poly, coef, verbose, FILE_MODE)

	renderer.draw_subplots()

def chaikin_animation(renderer : Renderer, poly : Polyhedron, n : int, coef : float, alpha : float = .6) -> None:
	frames : list[go.Frame] = []
	old_poly = Polyhedron(poly.nodes.copy())
	for gen in range(n):
		print('Generation: {}'.format(gen))
		alpha_poly_dd = renderer.get_polyhedron_draw_data(poly, alpha = alpha, color = polygon_color)
		if smc: main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', line_color = main_conn_color, node_color = node_color)
		else: main_conn_dd = []
		if sgc: graphical_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'graphical', line_color = graph_conn_color, node_color = node_color)
		else: graphical_conn_dd = []
		frames.append(go.Frame(
			data=alpha_poly_dd + graphical_conn_dd + main_conn_dd,
			name='Chaikin Gen {}'.format(gen)
		))
		if gen < n: poly = Polyhedron.Chaikin3D(poly, coef, verbose, FILE_MODE)
	fig = go.Figure(frames=frames)
	# add first frame
	alpha_poly_dd = renderer.get_polyhedron_draw_data(poly, alpha = alpha, color = polygon_color)
	if smc: main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', line_color = main_conn_color, node_color = node_color)
	else: main_conn_dd = []
	if sgc: graphical_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'graphical', line_color = graph_conn_color, node_color = node_color)
	else: graphical_conn_dd = []
	#fig.add_trace(alpha_poly_dd + graphical_conn_dd + main_conn_dd)
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


# Main function
def main():
	# create a renderer
	renderer = Renderer()

	# input file
	if input_file:
		reader = WaveFrontReader(input_file, True, rotate_mesh, verbose)
		poly = reader.to_polyhedron()

	# evaluate
	if evaluation_string:
		# evaluate the code
		eval(evaluation_string)
		# checks on the "poly" variable
		if 'poly' not in vars():
			raise Exception('You have to define a variable named "poly" in your evaluation string, when not giving an input file')
		if type(poly) != Polyhedron:
			raise TypeError('The "poly" variable does not have the type "Polyhedron"')

	# do we have a polyhedron
	if not input_file and not evaluation_string:
		raise Exception('You have to give a polyhedron! Either through the "-i", "-e" or both options! (cf. README)')

	# do chaikin generations before any graphics ?
	if plot != 'evolution' and plot != 'animation':
		assert chaikin_gens >= 0
		for _ in range(chaikin_gens):
			print(' - 3D Chaikin -')
			poly = Polyhedron.Chaikin3D(poly, chaikin_coef, verbose)
			print('Chaikin done')

	# switch the plot type
	if plot == 'simple':
		poly_dd = renderer.get_polyhedron_draw_data(poly, type_ = 'any', alpha = alpha, color = polygon_color)
		if smc: main_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'main', line_color = main_conn_color, node_color = node_color)
		else: main_conn_dd = []
		if sgc: graphical_conn_dd = renderer.get_connections_draw_data(poly, type_ = 'graphical', line_color = graph_conn_color, node_color = node_color)
		else: graphical_conn_dd = []
		renderer.draw(poly_dd + graphical_conn_dd + main_conn_dd)
	elif plot == 'full':
		draw_full(renderer, poly)
	elif plot == 'evolution':
		draw_chaikin_evolution(renderer, poly, chaikin_gens, chaikin_coef, alpha)
	elif plot == 'animation':
	   chaikin_animation(renderer, poly, chaikin_gens, chaikin_coef, alpha)
	else:
		raise Exception('Unrecognized plot: "{}"'.format(plot))

if __name__ == '__main__':
	main()
