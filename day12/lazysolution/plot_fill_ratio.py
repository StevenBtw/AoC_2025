import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open("input.txt") as f:
    content = f.read()

parts = content.split("\n\n")
shapes = []
for i in range(6):
    shape_lines = parts[i].split("\n")[1:]  # skip "N:"
    shapes.append(sum(line.count("#") for line in shape_lines))

print(f"Shape sizes: {shapes}")

ratios = []
for line in parts[6].strip().split("\n"):
    dims, counts = line.split(": ")
    w, h = map(int, dims.split("x"))
    section_area = w * h
    counts = list(map(int, counts.split()))
    total_shape_area = sum(c * s for c, s in zip(counts, shapes))
    ratios.append(total_shape_area / section_area)

left = [r for r in ratios if r < 1.0]
right = [r for r in ratios if r >= 1.0]
avg_left = sum(left) / len(left)
avg_right = sum(right) / len(right)

plt.figure(figsize=(10, 5))
plt.hist(ratios, bins=50, edgecolor='black')
plt.axvline(x=avg_left, color='green', linestyle='--', label=f'Fits avg: {avg_left:.3f}')
plt.axvline(x=avg_right, color='red', linestyle='--', label=f'No fit avg: {avg_right:.3f}')
plt.text(avg_left, 320, str(len(left)), fontsize=20, ha='center', color='green')
plt.text(avg_right + 0.01, 320, str(len(right)), fontsize=20, ha='center', color='red')
plt.legend()
plt.xlabel("Shape area / Section area")
plt.ylabel("Count")
plt.title("Distribution of fill ratios")
plt.tight_layout()
plt.savefig("fill_ratio.png")
print(f"< 1.0: {len(left)} (avg {avg_left:.3f}), >= 1.0: {len(right)} (avg {avg_right:.3f})")
