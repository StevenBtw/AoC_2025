import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from solution import (
        parse_input, count_paths, compute_depths, get_all_nodes,
        count_paths_through_both
    )
    return compute_depths, count_paths, count_paths_through_both, get_all_nodes, parse_input


@app.cell
def _(parse_input):
    with open("input.txt") as f:
        graph = parse_input(f.read())
    return (graph,)


@app.cell
def _(mo):
    task_selector = mo.ui.dropdown(
        options=["Part 1", "Part 2"],
        value="Part 1",
        label="Select Task"
    )
    return (task_selector,)


@app.cell
def _(mo, task_selector):
    route_selector = mo.ui.radio(
        options=["All paths", "dac → fft", "fft → dac"],
        value="All paths",
        label="Route filter (Part 2 only)"
    ) if task_selector.value == "Part 2" else None
    return (route_selector,)


@app.cell
def _(mo):
    depth_slider = mo.ui.slider(
        start=0,
        stop=20,
        step=1,
        value=20,
        label="Max depth to show",
        show_value=True
    )
    return (depth_slider,)


@app.cell
def _(mo, task_selector, route_selector, depth_slider):
    controls = mo.hstack([
        task_selector,
        depth_slider,
        route_selector if route_selector else mo.md("")
    ], justify="start", gap=2)
    controls


@app.cell
def _(count_paths, graph, mo, task_selector, route_selector):
    if task_selector.value == "Part 1":
        result = count_paths(graph, "you", "out")
        result_md = mo.md(f"## Part 1 Result\n\nNumber of paths from `you` to `out`: **{result}**")
    else:
        dac_first = (count_paths(graph, "svr", "dac") *
                     count_paths(graph, "dac", "fft") *
                     count_paths(graph, "fft", "out"))
        fft_first = (count_paths(graph, "svr", "fft") *
                     count_paths(graph, "fft", "dac") *
                     count_paths(graph, "dac", "out"))
        total = dac_first + fft_first

        selected_route = route_selector.value if route_selector else "All paths"
        if selected_route == "dac → fft":
            shown = dac_first
        elif selected_route == "fft → dac":
            shown = fft_first
        else:
            shown = total

        result_md = mo.md(
            f"## Part 2 Result\n\n"
            f"**Total paths:** {total}\n\n"
            f"- via dac→fft: {dac_first}\n"
            f"- via fft→dac: {fft_first}\n\n"
            f"**Currently showing:** {shown} paths"
        )
    return (result_md,)


@app.cell
def _(result_md):
    result_md
    return


@app.cell
def _(count_paths, compute_depths, get_all_nodes, graph, task_selector, depth_slider, route_selector):
    import altair as alt
    import pandas as pd
    import math

    start_node = "you" if task_selector.value == "Part 1" else "svr"
    end_node = "out"
    key_nodes = ["dac", "fft"] if task_selector.value == "Part 2" else []
    route = route_selector.value if route_selector else "All paths"

    depths = compute_depths(graph, start_node)
    all_nodes = get_all_nodes(graph)
    max_d = max(depths.values()) if depths else 0
    visible_depth = min(depth_slider.value, max_d)

    def get_nodes_on_route(start, via1, via2, end):
        nodes_on_path = set()
        d1 = compute_depths(graph, start)
        d2 = compute_depths(graph, via1)
        d3 = compute_depths(graph, via2)
        reverse_graph = {}
        for n, children in graph.items():
            for c in children:
                if c not in reverse_graph:
                    reverse_graph[c] = []
                reverse_graph[c].append(n)
        for n in all_nodes:
            if n in d1 and count_paths(graph, n, via1) > 0:
                nodes_on_path.add(n)
        for n in all_nodes:
            if n in d2 and count_paths(graph, n, via2) > 0:
                nodes_on_path.add(n)
        for n in all_nodes:
            if n in d3 and count_paths(graph, n, end) > 0:
                nodes_on_path.add(n)
        return nodes_on_path

    if task_selector.value == "Part 2" and route != "All paths":
        if route == "dac → fft":
            highlighted_nodes = get_nodes_on_route("svr", "dac", "fft", "out")
        else:
            highlighted_nodes = get_nodes_on_route("svr", "fft", "dac", "out")
    else:
        highlighted_nodes = None

    def paths_to(target):
        memo = {}
        for node in all_nodes:
            count_paths(graph, node, target, memo)
        memo[target] = 1
        return memo

    paths_to_end = paths_to(end_node)

    node_flow = {}
    for node in all_nodes:
        if node in depths and paths_to_end.get(node, 0) > 0:
            node_flow[node] = paths_to_end.get(node, 0)
        else:
            node_flow[node] = 0

    layers = {}
    for node in all_nodes:
        if node not in depths:
            continue
        d = depths[node]
        if d not in layers:
            layers[d] = []
        layers[d].append(node)

    pos = {}
    for depth, nodes_list in layers.items():
        sorted_nodes = sorted(nodes_list, key=lambda n: -node_flow.get(n, 0))
        count = len(sorted_nodes)
        for i, node in enumerate(sorted_nodes):
            y = (i - (count - 1) / 2) * 0.8
            pos[node] = (depth, y)

    key_depths = {k: depths.get(k, -1) for k in key_nodes}

    for kn in key_nodes:
        if kn not in pos and kn in all_nodes:
            mid_depth = max_d // 2
            pos[kn] = (mid_depth, len(pos) * 0.5)

    node_data = []
    for node in all_nodes:
        if node not in pos:
            continue
        x, y = pos[node]
        d = depths.get(node, 0)

        is_special = node == start_node or node == end_node or node in key_nodes
        if d > visible_depth and not is_special:
            continue

        flow = node_flow.get(node, 0)
        log_flow = math.log10(flow + 1) if flow > 0 else 0
        on_route = highlighted_nodes is None or node in highlighted_nodes

        if node == start_node:
            node_type = "start"
        elif node == end_node:
            node_type = "end"
        elif node in key_nodes:
            node_type = "key"
        elif flow > 0 and on_route:
            node_type = "path"
        else:
            node_type = "inactive"

        node_data.append({
            "node": node, "x": x, "y": y, "depth": d,
            "flow": flow, "log_flow": log_flow, "type": node_type
        })

    edge_data = []
    for node, children in graph.items():
        if node not in pos:
            continue
        src_depth = depths.get(node, 0)
        if src_depth > visible_depth:
            continue
        for child in children:
            if child not in pos:
                continue
            child_depth = depths.get(child, 0)
            if child_depth > visible_depth:
                continue
            x1, y1 = pos[node]
            x2, y2 = pos[child]
            edge_flow = min(node_flow.get(node, 0), node_flow.get(child, 0))

            on_route = highlighted_nodes is None or (node in highlighted_nodes and child in highlighted_nodes)
            is_active = edge_flow > 0 and on_route

            edge_data.append({
                "x": x1, "y": y1, "x2": x2, "y2": y2,
                "flow": edge_flow,
                "active": is_active,
                "src_depth": src_depth
            })

    nodes_df = pd.DataFrame(node_data)
    edges_df = pd.DataFrame(edge_data)
    return alt, nodes_df, edges_df, max_d, start_node, key_nodes, key_depths, visible_depth, pd


@app.cell
def _(alt, nodes_df, edges_df, max_d, start_node, key_nodes, key_depths, task_selector, visible_depth):
    inactive_edges = edges_df[~edges_df['active']]
    inactive_chart = alt.Chart(inactive_edges).mark_rule(
        strokeWidth=0.3, opacity=0.15
    ).encode(
        x=alt.X('x:Q', scale=alt.Scale(domain=[-0.5, max_d + 0.5]), axis=None),
        y=alt.Y('y:Q', axis=None),
        x2='x2:Q', y2='y2:Q',
        color=alt.value('#666')
    )

    active_edges = edges_df[edges_df['active']]
    active_chart = alt.Chart(active_edges).mark_rule(
        opacity=0.8
    ).encode(
        x='x:Q', y='y:Q', x2='x2:Q', y2='y2:Q',
        strokeWidth=alt.StrokeWidth(
            'flow:Q',
            scale=alt.Scale(type='log', range=[0.8, 4]),
            legend=None
        ),
        color=alt.Color(
            'flow:Q',
            scale=alt.Scale(type='log', scheme='turbo'),
            legend=None
        )
    )

    inactive_nodes = nodes_df[nodes_df['type'] == 'inactive']
    inactive_nodes_chart = alt.Chart(inactive_nodes).mark_circle(
        opacity=0.2, color='#888'
    ).encode(
        x='x:Q', y='y:Q',
        size=alt.value(15),
        tooltip=['node']
    )

    path_nodes = nodes_df[nodes_df['type'] == 'path']
    path_nodes_chart = alt.Chart(path_nodes).mark_circle().encode(
        x='x:Q', y='y:Q',
        size=alt.Size('log_flow:Q', scale=alt.Scale(range=[20, 80]), legend=None),
        color=alt.Color('flow:Q', scale=alt.Scale(type='log', scheme='plasma'), legend=None),
        tooltip=['node', 'flow', 'depth']
    )

    key_node_data = nodes_df[nodes_df['type'] == 'key']
    key_nodes_chart = alt.Chart(key_node_data).mark_circle(
        stroke='white', strokeWidth=2
    ).encode(
        x='x:Q', y='y:Q',
        size=alt.value(200),
        color=alt.value('#ff6b00'),
        tooltip=['node', 'flow']
    )
    key_labels = alt.Chart(key_node_data).mark_text(
        dy=-18, fontSize=11, fontWeight='bold', color='#ff6b00'
    ).encode(x='x:Q', y='y:Q', text='node:N')

    start_data = nodes_df[nodes_df['type'] == 'start']
    start_chart = alt.Chart(start_data).mark_circle(
        stroke='white', strokeWidth=2
    ).encode(
        x='x:Q', y='y:Q',
        size=alt.value(300),
        color=alt.value('limegreen'),
        tooltip=['node', 'flow']
    )
    start_label = alt.Chart(start_data).mark_text(
        dy=-20, fontSize=14, fontWeight='bold', color='limegreen'
    ).encode(x='x:Q', y='y:Q', text='node:N')

    end_data = nodes_df[nodes_df['type'] == 'end']
    end_chart = alt.Chart(end_data).mark_circle(
        stroke='white', strokeWidth=2
    ).encode(
        x='x:Q', y='y:Q',
        size=alt.value(300),
        color=alt.value('#ff3366'),
        tooltip=['node', 'flow']
    )
    end_label = alt.Chart(end_data).mark_text(
        dy=-20, fontSize=14, fontWeight='bold', color='#ff3366'
    ).encode(x='x:Q', y='y:Q', text='node:N')

    title = f"Part {'1' if task_selector.value == 'Part 1' else '2'}: {start_node} → out"
    if key_nodes and key_depths:
        key_info = ', '.join(f"{k}@{key_depths.get(k, '?')}" for k in key_nodes)
        title += f" (via {key_info})"
    title += f" | Depth: {visible_depth}/{max_d}"

    chart = (
        inactive_chart + active_chart +
        inactive_nodes_chart + path_nodes_chart +
        key_nodes_chart + key_labels +
        start_chart + start_label +
        end_chart + end_label
    ).properties(
        width=900, height=550,
        title=alt.TitleParams(title, fontSize=16),
        background='#1a1a2e'
    ).configure_view(strokeWidth=0)

    chart


if __name__ == "__main__":
    app.run()
