from networkx.utils.union_find import UnionFind
from itertools import combinations
from collections import Counter

with open("input.txt") as f:
    nodes = [tuple(map(int, line.strip().split(","))) for line in f]

edges = []
for (u, pos_u), (v, pos_v) in combinations(enumerate(nodes), 2):
    weight = sum((a - b) ** 2 for a, b in zip(pos_u, pos_v))
    edges.append((weight, u, v))

edges.sort()
uf = UnionFind(range(len(nodes)))

for weight, u, v in edges[:1000]:
    uf.union(u, v)

component_sizes = Counter(uf[node] for node in range(len(nodes)))
top3 = sorted(component_sizes.values(), reverse=True)[:3]

print(top3[0] * top3[1] * top3[2])
