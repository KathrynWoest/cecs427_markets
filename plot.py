import networkx as nx
import os
import webbrowser
import plotly.graph_objects as go

def plot(graph):
    """
    Creates a visualization of the market graph given its NetworkX format.

    Parameters
        - graph (nx.Graph): the original market graph
    
    Outputs
        - html file: the visualized graph
    """

    # Partitioning the graph into the two groups (A = "0", B = "1")
    A_nodes = [n for n, d in graph.nodes(data=True) if d.get("bipartite") == 0]
    B_nodes = [n for n, d in graph.nodes(data=True) if d.get("bipartite") == 1]

    # Computing bipartitle layout
    pos = nx.bipartite_layout(graph, A_nodes, align="vertical")

    # Building edge trace
    edge_x = []
    edge_y = []
    edge_hover_x = []
    edge_hover_y = []
    edge_hover_text = []

    for u, v, data in graph.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        # line segment
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

        # midpoint for hover markers/labels
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        edge_hover_x.append(mx)
        edge_hover_y.append(my)
        edge_hover_text.append(
            f"edge: {u} - {v}<br>"
            f"valuation: {data.get('valuation', 'NA')}"
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1),
        hoverinfo="skip",
        name="edges"
    )

    # Enabling hover for valuations
    edge_hover_trace = go.Scatter(
        x=edge_hover_x,
        y=edge_hover_y,
        mode="markers",
        marker=dict(size=10, opacity=0),
        text=edge_hover_text,
        hovertemplate="%{text}<extra></extra>",
        name="edge attributes"
    )

    # Creating valuation labels for edges
    edge_label_trace = go.Scatter(
        x=edge_hover_x,
        y=edge_hover_y,
        mode="text",
        text=[graph[u][v].get("valuation", "") for u, v in graph.edges()],
        textposition="middle center",
        hoverinfo="skip",
        name="valuation labels"
    )

    # Building node trace
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    node_symbol = []

    for n, data in graph.nodes(data=True):
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)

        price = data.get("price", 0)
        part = data.get("bipartite", None)

        # color by price
        node_color.append(price)

        # size by price (still visible when price = 0)
        node_size.append(18 + 6 * float(price))

        node_text.append(
            f"node: {n}<br>"
            f"partition: {part}<br>"
            f"price: {data.get('price', 'NA')}<br>"
            f"attrs: {data}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[str(n) for n in graph.nodes()],
        textposition="top center",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=node_text,
        marker=dict(
            size=node_size,
            color=node_color,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="price"),
            line=dict(width=1),
            symbol=node_symbol,
        ),
        name="nodes"
    )

    # Rendering figure
    fig = go.Figure(data=[edge_trace, edge_hover_trace, edge_label_trace, node_trace])

    fig.update_layout(
        title="Bipartite Market Graph",
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
    )

    # Generating figure
    file_path = os.path.abspath("market_graph.html")
    fig.write_html("market_graph.html", auto_open=False)
    webbrowser.open("file://" + file_path)
