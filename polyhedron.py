#
from __future__ import annotations
import node as N
import connection as C
import matrix
import sys, time
from dataholders import VirtualDict, VirtualSet
from copy import deepcopy

matrix.EPSILON = 10e-6
VERBOSE_STEP = 10

class Polyhedron:
	def __init__(self, nodes : list[N.Node], groups : VirtualSet = None):
		self.nodes = nodes
		self.groups = groups

	def __str__(self):
		return '\n* '.join(map(str, self.nodes))

	def __len__(self):
		return len(self.nodes)

	def __getitem__(self, index : int):
		return self.nodes[index]

	def __iter__(self):
		return iter(self._iter_triangles())

	def _iter_triangles(self, type_ : str = 'any') -> VirtualSet:
		triangle_set = VirtualSet()
		for node in self.nodes:
			for triangle in node.get_triangles(type_):
				# add the triangle. if there is alreadw this triangle in the set, it will not be added
				triangle_set.add(triangle)
		print('num triangles (' + str(type_) + ')', triangle_set.size)
		return triangle_set

	def _set_recursion_limit(self):
		sys.setrecursionlimit(10**6)

	def get_connections(self, type_ : str = 'any') -> list[C.Connection]:
		connection_list = []
		for node in self.nodes:
			for conn in node.get_connections_by_type(type_):
				if conn not in connection_list:
					connection_list.append(conn)
		print('num connections (' + type_ + ')', len(connection_list))
		return connection_list

	@staticmethod
	def _triangle_in_list(triangle_list, triangle) -> bool:
		if triangle in triangle_list: return True
		for other_triangle in triangle_list:
			if triangle[0] in other_triangle and triangle[1] in other_triangle and triangle[2] in other_triangle:
				return True
		return False

	@staticmethod
	def unique_triangles(triangles):
		index = 0
		length = len(triangles)
		while index < length:
			triangle = triangles.pop(index) # pop it from the list
			if Polyhedron._triangle_in_list(triangles, triangle):
				length -= 1
			else:
				# add it back and go one forward
				triangles.insert(index, triangle)
				index += 1
		return triangles

	@staticmethod
	def from_standard_vertex_lists(vertex_list : list[list[float]], vertex_index_list : list[list[int]]) -> Polyhedron:
		# build nodes
		nodes : list[N.Node] = list(map(N.Node.from_point, vertex_list))
		groups : VirtualSet = VirtualSet()
		to_connect = []
		# connect using the index list
		for i in range(len(vertex_index_list)):
			# get the indices
			node_groupe_index_list = vertex_index_list[i]
			# get the corresponding (ordered) group
			group = Group([nodes[index] for index in node_groupe_index_list])
			# connect the main connections (circular connection)
			group.cycle_connect('main')
			# order the group (should already be orderer tho -> else the cycle connection would fuck everything up)
			group.order()
			# connect later
			if group.size > 3:
				to_connect.append(group)
			# add group to list
			groups.add(group)

		# connect later
		for ogroup in to_connect:
			# connect the graphical connections
			ogroup.inter_connect('graphical', order_first = True)

		# return polyhedron
		return Polyhedron(nodes, groups)

	@staticmethod
	def Chaikin3D(polyhedron : Polyhedron, n : int = 4, verbose : bool = False) -> Polyhedron:
		'''ratio could also be float ?
		'''
		# change recursion limit
		polyhedron._set_recursion_limit()
		t1 = time.perf_counter()
		# init
		base_ratio = (n - 1) / n
		special_ratio = (n - 2) / (n - 1) # when the vector has already been trunced once
		node_virt_dict : VirtualDict = VirtualDict()
		new_connections : list[C.Connection] = []

		if verbose: print('Copying polyhedron data...')
		#old_polyhedron = deepcopy(polyhedron)
		old_nodes = polyhedron.nodes#.copy()#old_polyhedron.nodes
		old_groups = polyhedron.groups#.copy()	#old_polyhedron.groups # if we don't want to make the method static, but return a new polyhedron without modifying this one, should need this !
		sub_node_count = 0

		final_group_set : VirtualSet = VirtualSet()

		#
		total_nodes = len(polyhedron.nodes)
		if verbose: print('Calculating new node positions for {} verticies'.format(total_nodes))
		for node_index,current_node in enumerate(polyhedron.nodes):
			if verbose and node_index % VERBOSE_STEP == 0: print('[{}/{}] calculated ({:.2f}%)'.format(node_index, total_nodes, 100 * node_index / total_nodes))
			#print('\ncurrent node:', current_node)
			# create sub-nodes
			num_new_connections = num_graphical_nodes = 0
			group_set : VirtualSet = VirtualSet()
			for conn in current_node.connection_list:
				if conn.type_ == 'main':
					#
					partner_node = conn.get_partner_node(current_node)
					#print('\n - partner', partner_node)

					# calculate new pos (calculations done from num_connections to current node)
					u = matrix.vector.vector(partner_node.coords, current_node.coords)
					# get the right coefficient
					if partner_node not in polyhedron.nodes: # partner is one of the new nodes (already has been truncated once)
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
					group_set.add(sub_node)
					num_new_connections += 1
				elif conn.type_ == 'graphical':
					continue
				else:
					raise Exception('Unknown connection type:', conn.type_)
			# connect all the sub-nodes together (might find something to avoid connection-crossing -> len(group_set) > 3)
			#print('group set', group_set)
			group = Group(group_set)
			# connect
			group.cycle_connect('main')
			# connect graphical together
			group.inter_connect('graphical', order_first = True)
			final_group_set.add(group)

			# add those sub-nodes to the new nodes virtual dict
			node_virt_dict[old_nodes[node_index]] = group_set
			sub_node_count += group_set.size

		# connect all the groups together
		group_objects : list[Group] = []
		total_groups = len(old_groups)
		if verbose: print('Reconnect the new nodes (using the old nodes as starting point)')
		for index,old_group in enumerate(old_groups):
			if verbose and index % VERBOSE_STEP == 0: print('[{}/{}] new groups found ({:.2f}%)'.format(index, total_groups, 100 * index / total_groups))
			new_group : VirtualSet = VirtualSet()
			for old_node in old_group:
				new_nodes = node_virt_dict[old_node]
				two_nodes = []
				for new_node in new_nodes:
					for other_old_node in old_group:
						if old_node != other_old_node and len([0 for other_new_node in node_virt_dict[other_old_node] if C.Connection.are_connected(new_node, other_new_node)]) > 0: # any([C.Connection.are_connected(new_node, other_new_node) for other_new_node in node_virt_dict[other_old_node]]): # 
							break
					else:
						continue
					# found
					two_nodes.append(new_node)
					# don't break because there are two new nodes per old node
				if len(two_nodes) == 2:
					new_group.add(two_nodes[0])
					new_group.add(two_nodes[1])
				else:
					print('Bizarre group found.')

			new_group = Group(new_group)
			if new_group not in group_objects:
				group_objects.append(new_group)
				final_group_set.add(new_group)

		total_groups = len(group_objects)
		if verbose: print('Ordering the groups ({})'.format(total_groups))
		#print('num raw groups:', len(group_objects))
		i = 0
		total = len(group_objects)
		for i,group in enumerate(group_objects):
			if verbose and i % VERBOSE_STEP == 0: print('[{}/{}] ordered ({:.2f}%)'.format(i, total_groups, 100 * i / total_groups))
			group.order()

		if verbose: print('Connecting the groups ({})'.format(total_groups))
		for i,group in enumerate(group_objects):
			if verbose and i % VERBOSE_STEP == 0: print('[{}/{}] connected ({:.2f}%)'.format(i, total_groups, 100 * i / total_groups))
			group.inter_connect('graphical')

		# construct new node list
		if verbose: print('Building the new nodes list...')
		new_node_list : list[N.Node] = []
		for sub_nodes in node_virt_dict.values():
			new_node_list.extend(sub_nodes)

		# return the final polyhedron
		if verbose: print('Chaikin 3D iteration finished {} nodes in {:.3} sec'.format(total_nodes, time.perf_counter() - t1))
		return Polyhedron(new_node_list, final_group_set)

	@staticmethod
	def _nec_group_cond(group):
		assert type(group) == VirtualSet
		num_elements = group.size
		for i in range(num_elements):
			for j in range(i+1, num_elements):
				if not C.Connection.are_connected(group[i], group[j], 'main'):
					return False
		return True

	@staticmethod
	def _find_chaikin_groups_for_node(chaikin_node : N.Node) -> list[VirtualSet]:
		chaikin_group_set_list : list[VirtualSet] = []
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
					local_group_set_list : list[VirtualSet] = Polyhedron._rec_find_chaikin_group_with_plane(
						chaikin_node,
						end_node,
						second_node,
						partner_node,
						VirtualSet([end_node, chaikin_node, second_node]),
						plane
					)
					for local_group in local_group_set_list:
						if local_group not in chaikin_group_set_list:
							chaikin_group_set_list.append(local_group)

		return chaikin_group_set_list

	@staticmethod
	def _rec_find_chaikin_group_with_plane(start_node : N.Node, end_node : N.Node, second_node : N.Node, current_node : N.Node, current_group : VirtualSet, plane : matrix.Plane, depth : int = 0) -> list[VirtualSet]:

		# end of group ?
		if current_node == end_node:
			return [current_group]
		# invalid node ?
		if current_node in current_group or not plane.point_on_plane(current_node.coords):
			return []
		'''
		else:
			for i in range(len(current_group) - 1):
				if not C.Connection.are_connected(current_group[i], current_group[i + 1], 'main'):
					raise Exception('hm')
				if i > 2:
					if current_group[i].coords in map(lambda n: n.coords, list(current_group[:i]) + list(current_group[i+1:])):
						raise Exception('hm2')
			if not all([plane.point_on_plane(node.coords) for node in current_group]):
				print('yes')
			print(len(current_group))
		'''

		# add to group
		current_group.add(current_node)

		# continue search
		local_group_set_list : list[VirtualSet] = []
		for conn in current_node.get_connections_by_type('main'):
			partner_node = conn.get_partner_node(current_node)
			# sub_local_group_set_list are the chaikin groups that go through the partner_node (long & complicated name for something very simple)
			sub_local_group_set_list = Polyhedron._rec_find_chaikin_group_with_plane(
				start_node,
				end_node,
				second_node,
				partner_node,
				current_group.copy(),
				plane,
				depth + 1
			)
			# add unique groups
			for group in sub_local_group_set_list:
				if group not in local_group_set_list:
					local_group_set_list.append(group)

		return local_group_set_list

class Group:
	def __init__(self, iterable, do_order : bool = False):
		self.group = VirtualSet(iterable)
		self.ogroup = None
		self.ordered = False
		self.size = self.group.size
		#assert self.size > 2 # >= 3
		if do_order:
			self.order()

	def __str__(self) -> str:
		return '[{}] o: {} s: {}'.format(', '.join(map(str, self.group)), self.ordered, self.size)

	def __repr__(self) -> str:
		return str(self)

	def __len__(self):
		return self.size

	def __iter__(self):
		return iter(self.ogroup) if self.ordered else iter(self.group)

	def __getitem__(self, index : int):
		if self.ordered:
			return self.ogroup[index]
		return self.group[index]

	def order(self, force : bool = False) -> None:
		if not force and self.ordered: return
		# trivial case
		if self.size < 3:
			self.ogroup = self.group
			self.ordered = True
			return
		# initialize variables
		group_list : list[N.Node] = list(self.group)
		current_node = group_list.pop(0)
		self.ogroup = [current_node]
		# connect the next ones (don't care if we go 'left' or 'right')
		while group_list:
			for remaining_node in group_list:
				if C.Connection.are_connected(current_node, remaining_node, 'main'):
					self.ogroup.append(remaining_node)
					group_list.remove(remaining_node)
					current_node = remaining_node
					break
			else:
				print('current_node')
				_debug_print_full_node(current_node)
				print('group_list')
				_debug_print_full_nodes(group_list)
				print('ordered group')
				_debug_print_full_nodes(self.ogroup)
				print('group')
				_debug_print_full_nodes(self.group)
				raise Exception('broken group')
				print('Warning: broken group found. attaching remaning nodes: {}'.format(len(group_list)))
				self.ogroup.extend(group_list)
				break

		self.ordered = True

	def cycle_connect(self, connection_type : str = 'main') -> None:
		assert not self.ordered
		for i in range(self.size - 1):
			self.group[i].connect(self.group[i + 1], connection_type)
		self.group[-1].connect(self.group[0], connection_type)

	def inter_connect(self, connection_type : str = 'graphical', order_first : bool = False) -> None:
		if order_first: self.order(True)
		assert self.ordered
		num_iter = int(matrix.np.log2(self.size)) - 1
		#
		for x in range(num_iter):
			step = 2 ** (x + 1)
			#print('step:', step)
			prev_node = self.ogroup[0]
			for i in range(step, self.size, step):
				current_node = self.ogroup[i]
				prev_node.connect(current_node, connection_type)
				prev_node = current_node
			# connect last one to first one
			self.ogroup[0].connect(prev_node, connection_type)


def _debug_print_full_node(node, num_tabs = 0):
	prefix = '\t' * num_tabs
	print(f'{prefix}{str(node)}:')
	print(f'{prefix} main :')
	for conn in node.get_connections_by_type('main'):
		print(f'{prefix}\t - {str(conn)}')
	print(f'{prefix} graphical :')
	for conn in node.get_connections_by_type('graphical'):
		print(f'{prefix}\t - {str(conn)}')


def _debug_print_full_nodes(nodes, num_tabs = 0):
	prefix = '\t' * num_tabs
	print(f'{prefix}Num nodes: {len(nodes)}')
	for node in nodes:
		_debug_print_full_node(node, num_tabs + 1)
		print()





#
