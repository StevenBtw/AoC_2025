from itertools import combinations
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('dark_background')
from networkx.utils.union_find import UnionFind

script_dir = Path(__file__).parent
with open(script_dir / "input.txt") as f:
    nodes = [tuple(map(int, line.strip().split(","))) for line in f]

edges = []
for (u, pos_u), (v, pos_v) in combinations(enumerate(nodes), 2):
    weight = sum((a - b) ** 2 for a, b in zip(pos_u, pos_v))
    edges.append((weight, u, v))

edges.sort()

uf = UnionFind(range(len(nodes)))
for weight, u, v in edges[:1000]:
    uf.union(u, v)

components = [uf[i] for i in range(len(nodes))]
unique_components = list(set(components))
component_to_idx = {c: i for i, c in enumerate(unique_components)}
colors = [component_to_idx[c] for c in components]

xs = [n[0] for n in nodes]
ys = [n[1] for n in nodes]
zs = [n[2] for n in nodes]

# Plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(xs, ys, zs, c=colors, cmap='tab20', s=15, alpha=0.8)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title(f'Day 8 - Components after 1000 edges ({len(unique_components)} components)')

plt.tight_layout()
plt.savefig(script_dir / 'd8p1.png', dpi=150)
print(f"Saved to {script_dir / 'd8p1.png'}")
