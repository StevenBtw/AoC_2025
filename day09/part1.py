from ortools.sat.python import cp_model

with open("input.txt") as f:
    tiles = [tuple(map(int, line.strip().split(','))) for line in f if line.strip()]

model = cp_model.CpModel()
n = len(tiles)
xs, ys = [t[0] for t in tiles], [t[1] for t in tiles]

i = model.new_int_var(0, n - 1, 'i')
j = model.new_int_var(0, n - 1, 'j')
model.add(i < j)

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
