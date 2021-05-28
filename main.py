#

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

	'''
	poly = Polygon.from_triangular_points((
		(0,0,0), # A   0
		(1,0,0), # B   1
		(1,0,1), # C   2
		(1,1,0), # D   3
		(1,1,1), # E   4
		(0,1,0), # F   5
		(0,0,0), # A'  6
		(1,0,0), # B'  7
		(0,1,1), # G   9
		(0,0,1), # H   9
		(0,0,0), # A' 10
		(1,0,1), # C' 11
		(1,1,1), # E' 12
	),
	(
		7, # F -> B
		12,# H -> E
	),
	True,
	False)
	'''

	poly = Polygon.from_raw_points((
		(0,0,0), #  0 A
		(1,0,0), #  1 B
		(1,0,1), #  2 C
		(0,0,0), #  3 A'
		(0,0,1), #  4 D
		(0,0,0), #  5 A'
		(0,1,1), #  6 E
		(0,0,0), #  7 A'
		(0,1,0), #  8 F
		(0,0,0), #  9 A'
		(1,0,0), # 10 B'
		(1,1,0), # 11 G
		(0,1,1), # 12 E'
		(1,0,0), # 13 B'
		(1,0,1), # 14 C'
		(1,1,1), # 15 H
		(0,1,1), # 16 E'
		(1,0,1), # 17 C'
		(0,0,1), # 18 D'
	),
	(
		3,  # C -> A
		7,  # E -> A
		10, # F -> B
		12, # G -> E
		14, # G -> C
		18, # H -> D
	),
	True,
	False)

	'''
	A = (0,0,0)
	B = (1,0,0)
	C = (.5,1,0)
	D = (.5,.2,1)

	poly = Polygon.from_raw_points((
		A,#
		B,#
		C,#
		A,

		D,#
		B,
		A,
	),
	(),
	True,
	False)
	'''

	DO_CHAIKIN = 1

	if DO_CHAIKIN:
		print(' - 3D Chaikin -')
		poly = Polygon.Chaikin3D(poly)

	print(' - drawing -')
	renderer.draw_polygon(poly, alpha = 1, draw_text = False)
	return poly

if __name__ == '__main__':
	main()

