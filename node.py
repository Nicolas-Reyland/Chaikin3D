#
from __future__ import annotations
import connection as C

_hash_exp_1 = 12
_hash_exp_2 = 34
_hash_exp_3 = 5

def _cantor_pairing(a : float, b : float) -> float:
	return .5 * (a + b) * (a + b + 1) + b

class Node:
	def __init__(self, x : float, y : float, z : float):
		self.x, self.y, self.z = x, y, z
		self.num_connections : int = 0
		self.connection_list : list[C.Connection] = []
		self.coords = [self.x, self.y, self.z]

	def __hash__(self) -> int:
		return int(_cantor_pairing(_cantor_pairing(self.x, self.y), self.z) * 10e6)
		'''
		return int('{num}123{x}00{y}00{z}'.format(
			x = int(self.x ** _hash_exp_1),
			y = int(self.y ** _hash_exp_2),
			z = int(self.z ** _hash_exp_3),
			num = self.num_connections
		))
		'''

	def __eq__(self, other : Node) -> bool:
		return self.x == other.x and \
				self.y == other.y and \
				self.z == other.z and \
				self.num_connections == other.num_connections

	def __str__(self) -> str:
		return f'[({self.x:.2f},{self.y:.2f},{self.z:.2f}); num_connections = {self.num_connections}]'

	def connect(self, other : Node, type_ : str):# = 'main'):
		# check for already existing connection
		if C.Connection.are_connected(self, other):
			return
		# create connection
		conn = C.Connection(self, other, type_)
		# add to self
		self.connection_list.append(conn)
		self.num_connections += 1
		# add to other
		other.connection_list.append(conn)
		other.num_connections += 1

	def get_connections_by_type(self, type_ : str):
		if type_ == 'any': return self.connection_list
		return list(filter(lambda conn: conn.type_ == type_, self.connection_list))

	def get_triplets(self, type_ : str = 'any'):
		triplets = []
		for conn in self.get_connections_by_type(type_):
			# find the other, "partner", node in the connection
			conn_node = conn.get_partner_node(self)
			# find triangular connection_list
			for sub_conn in filter(lambda sub_conn: not sub_conn.contains_node(self), conn_node.get_connections_by_type(type_)):
				sub_conn_node = sub_conn.get_partner_node(conn_node)
				if C.Connection.are_connected(sub_conn_node, self, type_):
					triplets.append([
						self.coords,
						conn_node.coords,
						sub_conn_node.coords
					])
		return triplets

	def get_node_triplets(self, type_ : str = 'any'):
		triplets = []
		for conn in self.get_connections_by_type(type_):
			# find the other, "partner", node in the connection
			conn_node = conn.get_partner_node(self)
			# find triangular connection_list
			for sub_conn in filter(lambda sub_conn: not sub_conn.contains_node(self), conn_node.get_connections_by_type(type_)):
				sub_conn_node = sub_conn.get_partner_node(conn_node)
				if C.Connection.are_connected(sub_conn_node, self, type_):
					triplets.append([
						self,
						conn_node,
						sub_conn_node
					])
		return triplets

	@staticmethod
	def from_point(point : list[float]) -> Node:
		assert len(point) == 3
		return Node(point[0], point[1], point[2])
