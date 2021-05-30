#
from __future__ import annotations
from polygon import Polygon

def cube():
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

	return poly

def triangle():
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

	return poly

