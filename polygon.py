#
from __future__ import annotations
import node as N
import connection as C
import matrix
import sys
from copy import deepcopy

matrix.EPSILON = 10e-6

class Polygon:
	def __init__(self, nodes : list[N.Node], vertex_list = None, vertex_index_list = None):
		self.nodes = nodes
		self.vertex_list = vertex_list
		self.vertex_index_list = vertex_index_list

	def __str__(self):
		return '\n* '.join(map(str, self.nodes))

	def __len__(self):
		return len(self.nodes)

	def __getitem__(self, index : int):
		return self.nodes[index]

	def __iter__(self):
		return iter(self._hash_iter_triplets())

	def _iter_triplets(self, type_ : str = 'any'):
		triplet_list = []
		for node in self.nodes:
			for triplet in node.get_triplets(type_):
				# check unique-ness
				if Polygon._triplet_in_list(triplet_list, triplet):
					continue
				# it is unique, so we can add it to the list
				triplet_list.append(triplet)
		print('num triplets', len(triplet_list))
		return triplet_list

	def _hash_iter_triplets(self, type_ : str = 'any'):
		triplet_list = []
		triplet_hash_set = set()
		triplet_hash_func = lambda triplet: sum([sum([int(triplet[i][j] * 10e3) ** (j + 3) for j in range(3)]) for i in range(3)]) # pay atention to when a triplet is unique !
		for node in self.nodes:
			for triplet in node.get_triplets(type_):
				# check unique-ness
				triplet_hash = triplet_hash_func(triplet)
				if triplet_hash in triplet_hash_set:
					continue
				triplet_hash_set.add(triplet_hash)
				# it is unique, so we can add it to the list
				triplet_list.append(triplet)
		print('num hash triplets', len(triplet_hash_set))
		return triplet_list

	def _set_recursion_limit(self):
		sys.setrecursionlimit(10**6)

	def get_connections(self, type_ : str = 'any') -> list[C.Connection]:
		connection_list = []
		for node in self.nodes:
			for conn in node.get_connections_by_type(type_):
				if conn not in connection_list:
					connection_list.append(conn)
		print('num connections', len(connection_list))
		return connection_list

	@staticmethod
	def _triplet_in_list(triplet_list, triplet) -> bool:
		if triplet in triplet_list: return True
		for other_triplet in triplet_list:
			if triplet[0] in other_triplet and triplet[1] in other_triplet and triplet[2] in other_triplet:
				return True
		return False

	@staticmethod
	def unique_triplets(triplets):
		index = 0
		length = len(triplets)
		while index < length:
			triplet = triplets.pop(index) # pop it from the list
			if Polygon._triplet_in_list(triplets, triplet):
				length -= 1
			else:
				# add it back and go one forward
				triplets.insert(index, triplet)
				index += 1
		return triplets

	@staticmethod
	def from_raw_points(points : list[tuple[float]], index_list : list[int], inverse_index_list : bool = False, connect_endpoints : bool = True) -> Polygon:
		'''
		'''
		nodes : list[N.Node] = []
		num_points = len(points)
		processed_points = []
		index = num_nodes = 0
		if inverse_index_list:
			index_set = set(range(len(points))) # all indexes
			index_set -= set(index_list) # remove those from the initially given index_list
			index_list = list(index_set) # reassign index_list
		# process all points at least once
		while index < num_points:
			if index in index_list:
				connection_type = 'main'
			else:
				connection_type = 'graphical'
			current = points[index]
			#print('doing', current, 'conn type:', connection_type)
			node = N.Node(current[0], current[1], current[2])
			# check for reconnection
			if current in processed_points:
				point_index = processed_points.index(current)
				connect_node = nodes[point_index]
				connect_node.connect(nodes[-1], connection_type)
				index += 1
				#print('already processed point:', connect_node, '&', nodes[-1])
				continue
			# connect
			if num_nodes > 0:
				node.connect(nodes[-1], connection_type)
				#print('-1 connected', node, 'with', nodes[-1])

			# append
			nodes.append(node)
			processed_points.append(current)
			num_nodes += 1
			# incr index
			index += 1
		# process edge-points (non yet-connected)
		if connect_endpoints:
			#print('connecting endpoints')
			last_node = nodes[-1]
			for node in filter(lambda n: n.num_connections < 3, nodes[:-1]):
				node.connect(last_node, 'main')
				#print('connected last with', node)

		return Polygon(nodes)

	@staticmethod
	def from_triangular_points(points : list[tuple[float]], index_list : list[int], inverse_index_list : bool = False, connect_endpoints : bool = True) -> Polygon:
		'''Create a polygon object from an ordered list of (x,y,z) points/coordinates
		The index_list indicates all the "real" points of the polygon. All points that are not in this index_list will be understood
		as 'graphical connection points'. You an also choose to give the index_list of the graphical connection points only. You then
		have to specify the 'inverse_index_list' as being 'True'. This will inverse the list. If 'connect_endpoints' is
		set to true, the last point and the first point will be connected as a 'main' connection (non graphical)
		'''
		nodes : list[N.Node] = []
		num_points = len(points)
		processed_points = []
		index = num_nodes = 0
		if inverse_index_list:
			index_set = set(range(len(points))) # all indexes
			index_set -= set(index_list) # remove those from the initially given index_list
			index_list = list(index_set) # reassign index_list
		# process all points at least once
		while index < num_points:
			if index in index_list:
				connection_type = 'main'
			else:
				connection_type = 'graphical'
			current = points[index]
			#print('doing', current, 'conn type:', connection_type)
			node = N.Node(current[0], current[1], current[2])
			# check for reconnection
			if current in processed_points:
				point_index = processed_points.index(current)
				connect_node = nodes[point_index]
				connect_node.connect(nodes[-1], connection_type)
				index += 1
				#print('not a main connection:', connect_node, '&', nodes[-1])
				continue
			# connect
			if num_nodes > 0:
				node.connect(nodes[-1], connection_type)
				#print('-1 connected', node, 'with', nodes[-1])
				if num_nodes > 1:
					node.connect(nodes[-2], connection_type)
					#print('-2 connected', node, 'with', nodes[-2])
			# append
			nodes.append(node)
			processed_points.append(current)
			num_nodes += 1
			# incr index
			index += 1
		# process edge-points (non yet-connected)
		if connect_endpoints:
			#print('connecting endpoints')
			last_node = nodes[-1]
			for node in filter(lambda n: n.num_connections < 3, nodes[:-1]):
				node.connect(last_node, 'main')
				#print('connected last with', node)

		return Polygon(nodes)

	@staticmethod
	def from_standard_vertex_lists(vertex_list : list[list[float]], vertex_index_list : list[list[int]]) -> Polygon:
		# build nodes
		nodes : list[N.Node] = list(map(N.Node.from_point, vertex_list))
		# connect using the index list
		for index in range(len(vertex_index_list)):
			vertex_index = vertex_index_list[index]
			vertex_index[0] -= 1
			vertex_index[1] -= 1
			vertex_index[2] -= 1
			vertex_index_list[index] = vertex_index
			i, j, k = vertex_index
			A = nodes[i]
			B = nodes[j]
			C = nodes[k]
			A.connect(B, 'main')
			B.connect(C, 'main')
			C.connect(A, 'main')
		# return polygon
		return Polygon(nodes, vertex_list, vertex_index_list)

	@staticmethod
	def Chaikin3D(polygon : Polygon, n : int = 4) -> Polygon:
		'''ratio could also be float ?
		'''
		# change recursion limit
		polygon._set_recursion_limit()
		# init
		base_ratio = (n - 1) / n
		special_ratio = (n - 2) / (n - 1) # when the vector has already been trunced once
		node_dict : dict[N.Node, list[N.Node]] = dict()
		new_connections : list[C.Connection] = []

		old_nodes = deepcopy(polygon.nodes)

		sub_node_count = 0

		#
		for node_index,current_node in enumerate(polygon.nodes):
			#print('\ncurrent node:', current_node)
			# create sub-nodes
			num_new_connections = num_graphical_nodes = 0
			sub_node_list : list[N.Node] = []
			graphical_connections : list[C.Connection] = []
			for conn in current_node.connection_list:
				if conn.type_ == 'main':
					#
					partner_node = conn.get_partner_node(current_node)
					#print('\n - partner', partner_node)

					# calculate new pos (calculations done from num_connections to current node)
					u = matrix.vector.vector(partner_node.coords, current_node.coords)
					# get the right coefficient
					if partner_node not in polygon.nodes: # partner is one of the new nodes (already has been truncated once)
						#print(' - special ratio')
						ratio = special_ratio
					else:
						ratio = base_ratio
					# new vector
					v : list[float] = matrix.vector.multiplication_k(u, ratio)
					w = matrix.vector.add(partner_node.coords, v)

					# create new N.Node & new Connection
					sub_node = N.Node.from_point(w)
					sub_conn = C.Connection(sub_node, partner_node, 'main')

					# re-connect connection to new node & vice-versa
					#print(' * test\n  ->', '\n  -> '.join(map(str, partner_node.connection_list)))
					conn.update_node(current_node, sub_node)
					sub_node.connection_list = [conn]
					sub_node.num_connections = 1
					#print(' * test\n  ->', '\n  -> '.join(map(str, partner_node.connection_list)))
					#print(' - sub_node:', sub_node)
					#print(' - sub_node connection:', ' ; '.join(map(str, sub_node.connection_list)))

					# add to list & increment num_new_connections
					#print(' - adding', sub_node)
					sub_node_list.append(sub_node)
					num_new_connections += 1
				elif conn.type_ == 'graphical':
					graphical_connections.append(conn)
					#print(' - added graphical connection:', conn)
				else:
					raise Exception('Unknown connection type:', conn.type_)
			# connect all the sub-nodes together (might find something to avoid connection-crossing -> len(sub_node_list) > 3)
			#print(' - num sub-nodes', num_new_connections)
			for i in range(num_new_connections - 1):
				for j in range(i + 1, num_new_connections):
					sub_node_list[i].connect(sub_node_list[j], 'main')

			# add those sub-nodes to the new nodes list
			node_dict[old_nodes[node_index]] = sub_node_list
			#print('sub-nodes:', len(sub_node_list))
			sub_node_count += len(sub_node_list)

		#print('sub_node_count', sub_node_count)

		#print('\nreconnection')
		# connect all the sub_nodes together
		#processed_triplets : list[list[tuple[float]]] = []
		chaikin_groups_list : list[set[N.Node]] = []

		for old_node in old_nodes:
			old_group_list : list[set[N.Node]] = Polygon._find_chaikin_groups_for_node(old_node)
			for old_group in old_group_list:
				new_group : set[N.Node] = set()
				for old_node in old_group:
					new_nodes = node_dict[old_node]
					for new_node in new_nodes:
						for other_old_node in old_group:
							if old_node != other_old_node and any([C.Connection.are_connected(new_node, other_new_node) for other_new_node in node_dict[other_old_node]]):
								break
						else:
							continue
						# found
						new_group.add(new_node)
						# don't break because there are two new nodes per old node
				if new_group not in chaikin_groups_list:
					chaikin_groups_list.append(new_group)

		#print('num raw groups:', len(chaikin_groups_list))
		ordered_groups : list[list[N.Node]] = list(map(Polygon._order_chaikin_group, chaikin_groups_list))

		for ogroup in ordered_groups:
			#print('ordered group', ogroup)
			Polygon._connect_ordered_chaikin_group(ogroup)

		# construct new node list
		new_node_list : list[N.Node] = []
		for _,sub_nodes in node_dict.items():
			new_node_list.extend(sub_nodes)

		#print('num nodes:', len(new_node_list))

		# return the final polygon
		return Polygon(new_node_list)

	@staticmethod
	def _find_chaikin_groups_for_node(chaikin_node : N.Node) -> list[set[N.Node]]:
		chaikin_group_set_list : list[set[N.Node]] = []
		main_connections = chaikin_node.get_connections_by_type('main')
		num_main_connections = len(main_connections)

		for i in range(num_main_connections):
			#
			second_node = main_connections[i].get_partner_node(chaikin_node)
			for j in range(num_main_connections):
				if i == j: continue
				#
				end_node = main_connections[j].get_partner_node(chaikin_node)
				plane = matrix.Plane.from_points(chaikin_node.coords, second_node.coords, end_node.coords)
				#
				for sub_conn in second_node.get_connections_by_type('main'):
					partner_node = sub_conn.get_partner_node(second_node)
					local_group_set_list : list[set[N.Node]] = Polygon._rec_find_chaikin_group_with_plane(
						chaikin_node,
						end_node,
						second_node,
						partner_node,
						{end_node, chaikin_node, second_node},
						plane
					)
					for local_group in local_group_set_list:
						if local_group not in chaikin_group_set_list:
							chaikin_group_set_list.append(local_group)

		return chaikin_group_set_list

	@staticmethod
	def _rec_find_chaikin_group_with_plane(start_node : N.Node, end_node : N.Node, second_node : N.Node, current_node : N.Node, current_group : set[N.Node], plane : matrix.Plane) -> list[set[N.Node]]:
		'''Same as the '_rec_find_chaikin_group' function, but uses plane geometry properties to check if the group is valid
		'''

		# end of group ?
		if current_node == end_node:
			return [current_group]
		# invalid node ?
		if current_node in current_group or not plane.point_on_plane(current_node.coords):
			return []

		# add to group
		current_group.add(current_node)

		# continue search
		local_group_set_list : list[set[N.Node]] = []
		for conn in current_node.get_connections_by_type('main'):
			partner_node = conn.get_partner_node(current_node)
			# sub_local_group_set_list are the chaikin groups that go through the partner_node (long & complicated name for something very simple)
			sub_local_group_set_list = Polygon._rec_find_chaikin_group_with_plane(
				start_node,
				end_node,
				second_node,
				partner_node,
				current_group.copy(),
				plane
			)
			# add unique groups
			for group in sub_local_group_set_list:
				if group not in local_group_set_list:
					local_group_set_list.append(group)

		return local_group_set_list

	@staticmethod
	def _rec_find_chaikin_group(start_node : N.Node, current_node : N.Node, current_group : set[N.Node]) -> list[set[N.Node]]:
		# found the start node again ?
		if current_node == start_node:
			return [current_group]
		if current_node in current_group:
			return []

		# add to group
		current_group.add(current_node)

		# continue search
		groups_list : list[set[N.Node]] = []
		for conn in current_node.get_connections_by_type('main'):
			partner_node = conn.get_partner_node(current_node)
			groups = Polygon._rec_find_chaikin_group(start_node, partner_node, current_group.copy())
			for group in groups:
				if group not in groups_list:
					groups_list.append(group)

		return groups_list

	@staticmethod
	def _connect_ordered_chaikin_group(ordered_group : list[N.Node], connection_type : str = 'graphical') -> None:
		length = len(ordered_group)
		num_iter = int(matrix.np.log2(length)) - 1
		#print('number of iterations: {} for {} nodes'.format(num_iter, length))
		for x in range(num_iter):
			step = 2 ** (x + 1)
			#print('step:', step)
			prev_node = ordered_group[0]
			for i in range(step, length, step):
				current_node = ordered_group[i]
				prev_node.connect(current_node, connection_type)
				prev_node = current_node
			# connect last one to first one
			ordered_group[0].connect(prev_node, 'graphical')

	@staticmethod
	def _order_chaikin_group(group_set : set[N.Node]) -> list[N.Node]:
		# initialize variables
		group_list : list[N.Node] = list(group_set)
		current_node = group_list.pop(0)
		ordered_group = [current_node]
		# connect the next ones (don't care if we go 'left' or 'right')
		while group_list:
			for remaining_node in group_list:
				if C.Connection.are_connected(current_node, remaining_node):
					ordered_group.append(remaining_node)
					group_list.remove(remaining_node)
					current_node = remaining_node
					break

		return ordered_group
