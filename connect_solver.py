import random

GRID_SIZE = 5
NUM_STATIONS = 4
BLANK_CHAR = "."
STATION_CHAR = "X"

def print_grid(grid):
	# NOTE: Only works for grids up to size=10
	print("   " + " ".join([str(i) for i in range(len(grid))]))
	for i in range(len(grid)):
		print(f"{i} [" + " ".join([str(x) for x in grid[i]]) + "]")


def generate_grid(gsize, n_stations):
	grid = [[BLANK_CHAR for i in range(gsize)] for j in range(gsize)]
	station_count = 0
	stations = []
	while station_count < n_stations:
		new_x = random.randint(0, gsize-1)
		new_y = random.randint(0, gsize-1)
		# print(f"Attempting new station: {new_x}, {new_y}")
		
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
			stations.append((new_x, new_y))
			station_count += 1

	print_grid(grid)

	return (grid, stations)


def calc_dist(p1, p2):
	return abs(p1[0] - p2[0]) + (abs(p1[1] - p2[1])) - 1


def grid_solve(stations):
	# Determine 1-pairs
	dists = []
	for i in range(0, len(stations)):
		for j in range(i+1, len(stations)):
			d = calc_dist(stations[i], stations[j])
			print(stations[i], stations[j], d)
			dists.append((d, i, j))


	# Get i-distance pairs
	# For each pair, calculate each possible combination blocks
	# Merge in any necessary path squares for each combination




grid, stations = generate_grid(GRID_SIZE, NUM_STATIONS)
grid_solve(stations)