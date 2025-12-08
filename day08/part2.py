from networkx.utils.union_find import UnionFind
from itertools import combinations

with open("input.txt") as f:
    nodes = [tuple(map(int, line.strip().split(","))) for line in f]

edges = []
for (u, pos_u), (v, pos_v) in combinations(enumerate(nodes), 2):
    weight = sum((a - b) ** 2 for a, b in zip(pos_u, pos_v))
    edges.append((weight, u, v))

edges.sort()
uf = UnionFind(range(len(nodes)))

for weight, u, v in edges:
    if uf[u] != uf[v]:
        uf.union(u, v)
        if len(set(uf[n] for n in range(len(nodes)))) == 1:

            print(nodes[u][0] * nodes[v][0])
            break
