from ortools.sat.python import cp_model

def parse_input(filename):
    with open(filename) as f:
        return [tuple(map(int, line.strip().split(','))) for line in f if line.strip()]

def build_polygon_edges(red_tiles):
    edges = []
    n = len(red_tiles)
    for i in range(n):
        x1, y1 = red_tiles[i]
        x2, y2 = red_tiles[(i + 1) % n]
        edges.append(((x1, y1), (x2, y2)))
    return edges

def point_in_polygon(x, y, edges):
    intersections = 0
    for (x1, y1), (x2, y2) in edges:
        if x1 == x2:
            if min(y1, y2) <= y <= max(y1, y2):
                if x1 == x:
                    return True
                if x1 > x and min(y1, y2) < y <= max(y1, y2):
                    intersections += 1
        else:
            if min(x1, x2) <= x <= max(x1, x2) and y == y1:
                return True
    return intersections % 2 == 1

def rectangle_inside_polygon(rx1, ry1, rx2, ry2, tiles, edges):
    red_set = set(tiles)
    corners = [(rx1, ry1), (rx1, ry2), (rx2, ry1), (rx2, ry2)]
    for cx, cy in corners:
        if (cx, cy) not in red_set and not point_in_polygon(cx, cy, edges):
            return False

    for vx, vy in tiles:
        if rx1 < vx < rx2 and ry1 < vy < ry2:
            return False
        
    for (ex1, ey1), (ex2, ey2) in edges:
        if ex1 == ex2:
            if rx1 < ex1 < rx2:
                edge_y_min, edge_y_max = min(ey1, ey2), max(ey1, ey2)
                if edge_y_min < ry2 and edge_y_max > ry1:
                    return False
        else:
            if ry1 < ey1 < ry2:
                edge_x_min, edge_x_max = min(ex1, ex2), max(ex1, ex2)
                if edge_x_min < rx2 and edge_x_max > rx1:
                    return False
    return True

def get_valid_pairs(tiles):
    edges = build_polygon_edges(tiles)
    n = len(tiles)
    valid = []

    for i in range(n):
        xi, yi = tiles[i]
        for j in range(i + 1, n):
            xj, yj = tiles[j]
            x1, x2 = min(xi, xj), max(xi, xj)
            y1, y2 = min(yi, yj), max(yi, yj)

            if rectangle_inside_polygon(x1, y1, x2, y2, tiles, edges):
                valid.append((i, j))
    return valid

with open("input.txt") as f:
    tiles = [tuple(map(int, line.strip().split(','))) for line in f if line.strip()]

valid_pairs = get_valid_pairs(tiles)

model = cp_model.CpModel()
n = len(tiles)
xs, ys = [t[0] for t in tiles], [t[1] for t in tiles]

i = model.new_int_var(0, n - 1, 'i')
j = model.new_int_var(0, n - 1, 'j')
model.add(i < j)

model.add_allowed_assignments([i, j], valid_pairs)
xi, xj = model.new_int_var(min(xs), max(xs), 'xi'), model.new_int_var(min(xs), max(xs), 'xj')
yi, yj = model.new_int_var(min(ys), max(ys), 'yi'), model.new_int_var(min(ys), max(ys), 'yj')
model.add_element(i, xs, xi)
model.add_element(i, ys, yi)
model.add_element(j, xs, xj)
model.add_element(j, ys, yj)

x1, x2 = model.new_int_var(min(xs), max(xs), 'x1'), model.new_int_var(min(xs), max(xs), 'x2')
y1, y2 = model.new_int_var(min(ys), max(ys), 'y1'), model.new_int_var(min(ys), max(ys), 'y2')
model.add_min_equality(x1, [xi, xj])
model.add_max_equality(x2, [xi, xj])
model.add_min_equality(y1, [yi, yj])
model.add_max_equality(y2, [yi, yj])

w, h = model.new_int_var(1, max(xs)-min(xs)+1, 'w'), model.new_int_var(1, max(ys)-min(ys)+1, 'h')
model.add(w == x2 - x1 + 1)
model.add(h == y2 - y1 + 1)
area = model.new_int_var(1, (max(xs)-min(xs)+1) * (max(ys)-min(ys)+1), 'area')
model.add_multiplication_equality(area, [w, h])
model.maximize(area)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(solver.value(area))
