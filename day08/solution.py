from collections import Counter
from itertools import combinations
from networkx.utils.union_find import UnionFind

with open("input.txt") as f:
    nodes = [tuple(map(int, line.strip().split(","))) for line in f]

edges = []
for (u, pos_u), (v, pos_v) in combinations(enumerate(nodes), 2):
    weight = sum((a - b) ** 2 for a, b in zip(pos_u, pos_v))
    edges.append((weight, u, v))

edges.sort()

uf1 = UnionFind(range(len(nodes)))
for weight, u, v in edges[:1000]:
    uf1.union(u, v)

component_sizes = Counter(uf1[node] for node in range(len(nodes)))
top3 = sorted(component_sizes.values(), reverse=True)[:3]
print("part1:", top3[0] * top3[1] * top3[2])

uf2 = UnionFind(range(len(nodes)))
for weight, u, v in edges:
    if uf2[u] != uf2[v]:
        uf2.union(u, v)
        if len(set(uf2[n] for n in range(len(nodes)))) == 1:
            print("part2:", nodes[u][0] * nodes[v][0])
            break
