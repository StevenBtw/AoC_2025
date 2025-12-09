from ortools.sat.python import cp_model

def parse_input(filename):
    with open(filename) as f:
        return [tuple(map(int, line.strip().split(','))) for line in f if line.strip()]

def build_polygon_edges(tiles):
    edges = []
    n = len(tiles)
    for i in range(n):
        x1, y1 = tiles[i]
        x2, y2 = tiles[(i + 1) % n]
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
    valid = set()
    for i in range(n):
        xi, yi = tiles[i]
        for j in range(i + 1, n):
            xj, yj = tiles[j]
            bx1, bx2 = min(xi, xj), max(xi, xj)
            by1, by2 = min(yi, yj), max(yi, yj)
            if rectangle_inside_polygon(bx1, by1, bx2, by2, tiles, edges):
                valid.add((i, j))
    return valid

def maximize_rectangle(tiles, part=1, callback_factory=None):
    model = cp_model.CpModel()
    n = len(tiles)
    selected = [model.new_bool_var(f's{i}') for i in range(n)]
    model.add(sum(selected) == 2)

    xs, ys = [t[0] for t in tiles], [t[1] for t in tiles]
    X1, X2, Y1, Y2 = min(xs), max(xs), min(ys), max(ys)

    x1 = model.new_int_var(X1, X2, 'x1')
    x2 = model.new_int_var(X1, X2, 'x2')
    y1 = model.new_int_var(Y1, Y2, 'y1')
    y2 = model.new_int_var(Y1, Y2, 'y2')

    for i, (x, y) in enumerate(tiles):
        model.add(x1 <= x).only_enforce_if(selected[i])
        model.add(x2 >= x).only_enforce_if(selected[i])
        model.add(y1 <= y).only_enforce_if(selected[i])
        model.add(y2 >= y).only_enforce_if(selected[i])

    for var, coord_idx in [(x1, 0), (x2, 0), (y1, 1), (y2, 1)]:
        touches = []
        for i, t in enumerate(tiles):
            b = model.new_bool_var(f't{var}_{i}')
            model.add(var == t[coord_idx]).only_enforce_if(b)
            model.add(selected[i] == 1).only_enforce_if(b)
            touches.append(b)
        model.add(sum(touches) >= 1)

    if part == 2:
        valid_pairs = get_valid_pairs(tiles)
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) not in valid_pairs:
                    model.add(selected[i] + selected[j] <= 1)

    width = model.new_int_var(1, X2 - X1 + 1, 'w')
    height = model.new_int_var(1, Y2 - Y1 + 1, 'h')
    model.add(width == x2 - x1 + 1)
    model.add(height == y2 - y1 + 1)
    area = model.new_int_var(1, (X2 - X1 + 1) * (Y2 - Y1 + 1), 'area')
    model.add_multiplication_equality(area, [width, height])
    model.maximize(area)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1  # Single thread = more intermediate solutions
    callback = callback_factory(selected, x1, x2, y1, y2) if callback_factory else None
    status = solver.solve(model, callback) if callback else solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            'status': 'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE',
            'area': int(solver.objective_value),
            'selected_tiles': [i for i in range(n) if solver.value(selected[i])],
            'rect': {'x1': solver.value(x1), 'x2': solver.value(x2),
                     'y1': solver.value(y1), 'y2': solver.value(y2)}
        }
    return None

if __name__ == "__main__":
    tiles = parse_input("input.txt")
    print("Part 1:", maximize_rectangle(tiles, part=1)['area'])
    print("Part 2:", maximize_rectangle(tiles, part=2)['area'])
