def parse_input(text):
    graph = {}
    for line in text.strip().splitlines():
        node, rest = line.split(": ")
        graph[node] = rest.split()
    return graph

def get_all_nodes(graph):
    nodes = set(graph.keys())
    for children in graph.values():
        nodes.update(children)
    return nodes

def compute_depths(graph, start="you"):
    depths = {start: 0}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for child in graph.get(node, []):
            if child not in depths:
                depths[child] = depths[node] + 1
                queue.append(child)
    return depths

def nodes_at_depth(depths, d):
    return [n for n, depth in depths.items() if depth == d]

def count_paths(graph, current, target, memo=None):
    if memo is None:
        memo = {}
    if current == target:
        return 1
    if current in memo:
        return memo[current]
    if current not in graph:
        return 0
    total = sum(count_paths(graph, child, target, memo) for child in graph[current])
    memo[current] = total
    return total

def get_edges_for_layer(graph, depths, layer):
    layer_nodes = nodes_at_depth(depths, layer)
    edges = []
    for node in layer_nodes:
        for child in graph.get(node, []):
            if depths.get(child) == layer + 1:
                edges.append((node, child))
    return edges

def paths_through_node(graph, node, target="out", memo=None):
    if memo is None:
        memo = {}
    return count_paths(graph, node, target, memo)

def edge_is_valid(graph, source, target, target_node="out"):
    return paths_through_node(graph, target, target_node) > 0

def compute_node_path_counts(graph, target="out"):
    memo = {}
    all_nodes = get_all_nodes(graph)
    for node in all_nodes:
        count_paths(graph, node, target, memo)
    memo[target] = 1
    return memo

def get_all_valid_edges(graph, depths, path_counts):
    valid = []
    max_depth = max(depths.values())
    for layer in range(max_depth):
        edges = get_edges_for_layer(graph, depths, layer)
        for s, t in edges:
            if path_counts.get(t, 0) > 0:
                valid.append((layer, s, t))
    return valid

def count_paths_through_both(graph, start, end, node1, node2):
    """Count paths from start to end that visit both node1 and node2."""
    # Paths: start → node1 → node2 → end
    path1 = (count_paths(graph, start, node1) *
             count_paths(graph, node1, node2) *
             count_paths(graph, node2, end))
    # Paths: start → node2 → node1 → end
    path2 = (count_paths(graph, start, node2) *
             count_paths(graph, node2, node1) *
             count_paths(graph, node1, end))
    return path1 + path2


if __name__ == "__main__":
    with open("input.txt") as f:
        graph = parse_input(f.read())
    print("Part 1:", count_paths(graph, "you", "out"))
    print("Part 2:", count_paths_through_both(graph, "svr", "out", "dac", "fft"))
