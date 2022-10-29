import random
import itertools
from copy import deepcopy
from time import sleep

GRID_SIZE = 15
NUM_STATIONS = 10
BLANK_CHAR = "."
STATION_CHAR = "X"
PATH_CHAR = "O"
POTENTIAL_CHAR = "?"
TIME_DELAY = 1.5


def print_grid(grid):
	"""Prints a grid matrix in human-readable format."""
	max_index = len(grid) - 1
	max_index_length = len(str(max_index))
	M = max_index_length

	print("  " + " "*M + " ".join([f"{i: >{M}}" for i in range(len(grid))]))
	for i in range(len(grid)):
		print(f"{i: >{M}} [" + " ".join([f"{x: >{M}}" for x in grid[i]]) + "]")
	print()


def print_solved_grid(grid, solution):
	"""Fills a grid with the solution path, then calls print_grid()."""
	solved_grid = deepcopy(grid)
	for y, x in solution:
		if solved_grid[y][x] != STATION_CHAR:
			solved_grid[y][x] = PATH_CHAR
	print_grid(solved_grid)


def print_interim_grid(grid, groups):
	interim_grid = deepcopy(grid)
	fixed_points = []
	potential_points = []

	for g in groups:
		gs = [set(perm) for perm in g]
		common_points = gs.pop().intersection(*gs)
		gs = [set(perm) for perm in g]
		all_points = gs.pop().union(*gs)
		fixed_points += list(common_points)
		potential_points += list(all_points - common_points)

	for y, x in fixed_points:
		if interim_grid[y][x] != STATION_CHAR:
			interim_grid[y][x] = PATH_CHAR

	for y, x in potential_points:
		interim_grid[y][x] = POTENTIAL_CHAR

	print_grid(interim_grid)

	# print(fixed_points)
	# print(potential_points)




def generate_grid(gsize, n_stations):
	"""Generate a square grid of side-length gsize, and populate it with
	n_station number of stations."""
	grid = [[BLANK_CHAR for i in range(gsize)] for j in range(gsize)]
	station_count = 0
	stations = []
	while station_count < n_stations:
		new_x = random.randint(0, gsize-1)
		new_y = random.randint(0, gsize-1)
		
		# Allow stations to be adjacent diagonally, but not vertically or horizontally
		valid_loc = True
		for dx, dy in ((0,0), (1,0), (-1,0), (0, 1), (0, -1)):
			cx = new_x + dx
			cy = new_y + dy

			if (cx < gsize) and (cx >= 0):
				if (cy < gsize) and (cy >= 0):
					if grid[cy][cx] == STATION_CHAR:
						valid_loc = False
						break

		if valid_loc:
			grid[new_y][new_x] = STATION_CHAR
			stations.append((new_y, new_x))
			station_count += 1

	return (grid, stations)


def calculate_point_distance(point1, point2):
	"""Calculate the number of intermediary points required to join two points."""
	return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1]) - 1


def calculate_permutation_distance(perm1, perm2):
	"""Calculate the minimum distance between two permutations (individual 
	possible paths of a group). Return the minimum distance, plus an array of 
	the points (one from each path) that this distance could be achieved from."""
	minimum_distance = GRID_SIZE**2
	best_points = []
	for point1 in perm1:
		for point2 in perm2:
			dist = calculate_point_distance(point1, point2)

			if dist < minimum_distance:
				best_points = []
				minimum_distance = dist

			if dist == minimum_distance:
				best_points.append(tuple(sorted([point1, point2])))

	return (minimum_distance, best_points)


def calculate_group_distance(group1, group2):
	"""Calculate the minimum distance between two groups (where a group is a 
	collection of permutations, or possible paths). Returns the minimum distance,
	and a list of permutation combinations (one from each group) that match this
	distance. The permutation combinations (as returned in the local variable 
	'valid_perms') are denoted as:
	* Index-for-permutation-of-group1,
	* Index-for-permutation-of-group2,
	* Array of possible best-points as returned from calculate_permutation_distance()"""
	minimum_distance = GRID_SIZE**2

	valid_perms = []

	for i in range(len(group1)):
		perm1 = group1[i]
		for j in range(len(group2)):
			perm2 = group2[j]

			dist, best_points = calculate_permutation_distance(perm1, perm2)
			
			if dist < minimum_distance:
				valid_perms = []
				minimum_distance = dist

			if dist == minimum_distance:
				valid_perms.append((i, j, best_points))

	return (minimum_distance, valid_perms)


def get_possible_paths(point1, point2):
	"""Get an array of all possible minimum-distance paths from point1 to point2
	(exclusive of those points)."""
	diff_y = abs(point1[0] - point2[0])
	diff_x = abs(point1[1] - point2[1])

	movements = []
	
	if point1[0] < point2[0]:
		movements += [(1, 0) for _ in range(diff_y)]
	else:
		movements += [(-1, 0) for _ in range(diff_y)]

	if point1[1] < point2[1]:
		movements += [(0, 1) for _ in range(diff_x)]
	else:
		movements += [(0, -1) for _ in range(diff_x)]

	step_sets = set(itertools.permutations(movements, len(movements)-1))

	path_set = []
	for steps in step_sets:
		path = []
		p = [*point1]
		for s in steps:
			p[0] += s[0]
			p[1] += s[1]
			path.append(tuple(p))
		path_set.append(path)

	return path_set


def grid_solve_step(groups):
	"""Find the two closest groups, and merge them together. Allow for multiple
	potential pathways, if necessary, that will collapse either when one becomes
	non-viable, or we reach the end (in which case we just pick one)."""
	results = []
	group_pairs = itertools.combinations(range(len(groups)), 2)

	for i, j in group_pairs:
		g1 = groups[i]
		g2 = groups[j]

		distance, valid_perms = calculate_group_distance(g1, g2)

		results.append((distance, i, j, valid_perms))

	results.sort()

	_, i, j, permutation_pairs = results[0]

	old_groups = [groups[k] for k in range(len(groups)) if k not in (i, j)]

	ng1 = groups[i]
	ng2 = groups[j]

	# print("OLD GROUPS:", old_groups)
	# print("COMBINED:", ng1, ng2)

	new_group = []

	for p in permutation_pairs:
		p1 = ng1[p[0]]
		p2 = ng2[p[1]]
		best_point_pairs = p[2]

		for point1, point2 in best_point_pairs:
			possible_paths = get_possible_paths(point1, point2)
			for path in possible_paths:
				new_group.append(p1 + p2 + path)

	groups = old_groups + [new_group]

	# print(groups)
	# print("GROUPS LEFT:", len(groups))

	return groups


def grid_solve(stations, show_steps=False):
	"""Call grid_solve_step() to merge groups until only one group is left. Then
	collapse any remaining potential paths to produce a final correct solution."""
	groups = [[[s]] for s in stations]

	while len(groups) > 1:
		groups = grid_solve_step(groups)
		if show_steps:
			print_interim_grid(grid, groups)
			sleep(TIME_DELAY)

	return groups[0][0]


if __name__ == "__main__":
	grid, stations = generate_grid(GRID_SIZE, NUM_STATIONS)
	print("Original Grid:")
	print_grid(grid)

	# Change to False here to skip visualisation of each step.
	solution = grid_solve(stations, True)

	print("Minimum Path Length:", len(solution)-len(stations))
	print_solved_grid(grid, solution)