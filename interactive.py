import networkx as nx
import plotly.graph_objects as go


def _get_groups(graph):
    """
    Helper function for identifying the buyer and seller groups from the graph.

    Parameters
        - graph (nx.Graph): the market graph

    Returns
        - tuple (buyers, sellers): each tuple is a list of node identifiers
    """

    sellers = []
    buyers = []

    seller_group = None
    buyer_group = None

    for node, price in graph.nodes(data="price"):
        if price is not None and seller_group is None:
            seller_group = graph.nodes[node]["bipartite"]
        elif price is None and buyer_group is None:
            buyer_group = graph.nodes[node]["bipartite"]

        if seller_group is not None and buyer_group is not None:
            break

    for node, bi in graph.nodes(data="bipartite"):
        if bi == seller_group:
            sellers.append(node)
        elif bi == buyer_group:
            buyers.append(node)

    return buyers, sellers


def _find_constricted_sellers(ps_graph, buyers, sellers):
    """
    Helper function to recompute the visited set from a stored preference-seller graph.

    Parameters
        - ps_graph (nx.Graph): the preference-seller graph
        - buyers ([]): list of buyer nodes
        - sellers ([]): list of seller nodes

    Returns
        - set of seller nodes in the constricted set. Returns an empty seet if no
        constricted set is identified (perfect matching).
    """

    starter = None
    for buyer in buyers:
        if buyer in ps_graph.nodes and not ps_graph.nodes[buyer].get("matched", False):
            starter = buyer
            break

    if starter is None:
        return set()

    bfs_layers = [[starter]]
    visited = {starter}
    layer = 0

    while layer < len(ps_graph.nodes()):
        next_layer = []

        if layer % 2 == 0:
            # unmatched edges only
            for node in bfs_layers[layer]:
                for u, v in ps_graph.edges(node):
                    other = u if v == node else v

                    if not ps_graph.edges[(u, v)].get("matched", False) and other not in visited:
                        next_layer.append(other)
                        visited.add(other)

                        if other in sellers and not ps_graph.nodes[other].get("matched", False):
                            return set()
        else:
            # matched edges only
            for node in bfs_layers[layer]:
                for u, v in ps_graph.edges(node):
                    other = u if v == node else v

                    if ps_graph.edges[(u, v)].get("matched", False) and other not in visited:
                        next_layer.append(other)
                        visited.add(other)

        if not next_layer:
            break

        bfs_layers.append(next_layer)
        layer += 1

    return {seller for seller in sellers if seller in visited}


def interactive(graph, round_results):
    """
    Build an animated Plotly figure showing the results of every round. Includes a scrubbing bar to 
    see each round's results, and a pause/play button to play the animation on a loop.

    Parameters
        - graph (nx.Graph): Original market graph
        - round_results (list[nx.Graph]): Output of analysis(graph), where each item is a saved preference-seller graph

    Returns
        - fig : plotly.graph_objects.Figure

    Raises
        - ValueError if no round data is provided
    """

    if not round_results:
        raise ValueError("round_results is empty.")

    buyers, sellers = _get_groups(graph)

    # fixed layout so nodes stay in the same place every frame
    pos = nx.bipartite_layout(graph, sellers, align="vertical")

    frames = []

    for i, ps_graph in enumerate(round_results):
        constricted = _find_constricted_sellers(ps_graph, buyers, sellers)

        matched_edge_x = []
        matched_edge_y = []
        unmatched_edge_x = []
        unmatched_edge_y = []

        edge_hover_x = []
        edge_hover_y = []
        edge_hover_text = []

        for u, v, data in ps_graph.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]

            if data.get("matched", False):
                matched_edge_x += [x0, x1, None]
                matched_edge_y += [y0, y1, None]
            else:
                unmatched_edge_x += [x0, x1, None]
                unmatched_edge_y += [y0, y1, None]

            seller = u if u in sellers else v
            buyer = v if seller == u else u

            valuation = graph.edges[(u, v)]["valuation"] if graph.has_edge(u, v) else graph.edges[(v, u)]["valuation"]
            price = ps_graph.nodes[seller].get("price", None)
            utility = valuation - price if price is not None else valuation

            edge_hover_x.append((x0 + x1) / 2)
            edge_hover_y.append((y0 + y1) / 2)
            edge_hover_text.append(
                f"seller: {seller}<br>"
                f"buyer: {buyer}<br>"
                f"valuation: {valuation}<br>"
                f"price: {price}<br>"
                f"valuation - price: {utility}<br>"
                f"matched: {data.get('matched', False)}"
            )

        unmatched_edge_trace = go.Scatter(
            x=unmatched_edge_x,
            y=unmatched_edge_y,
            mode="lines",
            line=dict(width=2, color="royalblue", dash="dot"),
            hoverinfo="skip",
            showlegend=False
        )

        matched_edge_trace = go.Scatter(
            x=matched_edge_x,
            y=matched_edge_y,
            mode="lines",
            line=dict(width=4, color="seagreen"),
            hoverinfo="skip",
            showlegend=False
        )

        edge_hover_trace = go.Scatter(
            x=edge_hover_x,
            y=edge_hover_y,
            mode="markers",
            marker=dict(size=10, opacity=0),
            customdata=edge_hover_text,
            hovertemplate="%{customdata}<extra></extra>",
            showlegend=False
        )

        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_symbol = []
        node_size = []

        for node in ps_graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            matched = ps_graph.nodes[node].get("matched", False)

            if node in sellers:
                price = ps_graph.nodes[node].get("price", None)

                if node in constricted:
                    color = "orange"
                elif matched:
                    color = "mediumseagreen"
                else:
                    color = "indianred"

                symbol = "square"
                text = (
                    f"seller: {node}<br>"
                    f"price: {price}<br>"
                    f"matched: {matched}<br>"
                    f"constricted set: {node in constricted}"
                )
            else:
                color = "mediumseagreen" if matched else "lightskyblue"
                symbol = "circle"
                text = (
                    f"buyer: {node}<br>"
                    f"matched: {matched}"
                )

            node_color.append(color)
            node_symbol.append(symbol)
            node_size.append(22)
            node_text.append(text)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=[str(n) for n in ps_graph.nodes()],
            textposition="top center",
            customdata=node_text,
            hovertemplate="%{customdata}<extra></extra>",
            marker=dict(
                size=node_size,
                color=node_color,
                symbol=node_symbol,
                line=dict(width=1, color="black")
            ),
            showlegend=False
        )

        if all(ps_graph.nodes[b].get("matched", False) for b in buyers):
            title = f"Round {i + 1}: perfect matching found"
        elif constricted:
            title = f"Round {i + 1}: constricted sellers highlighted"
        else:
            title = f"Round {i + 1}"

        frames.append(
            go.Frame(
                data=[unmatched_edge_trace, matched_edge_trace, edge_hover_trace, node_trace],
                name=str(i),
                layout=go.Layout(title=title)
            )
        )

    steps = []
    for i in range(len(frames)):
        steps.append(
            dict(
                method="animate",
                args=[
                    [str(i)],
                    {
                        "mode": "immediate",
                        "frame": {"duration": 0, "redraw": True},
                        "transition": {"duration": 0}
                    }
                ],
                label=str(i + 1)
            )
        )

    fig = go.Figure(data=frames[0].data, frames=frames)

    fig.update_layout(
        title=frames[0].layout.title.text if frames[0].layout.title else "Interactive Preference-seller Graph",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest",
        margin=dict(l=20, r=20, t=60, b=20),
        sliders=[
            dict(
                active=0,
                currentvalue={"prefix": "Round: "},
                pad={"t": 30},
                steps=steps
            )
        ],
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.1,
                y=0,
                showactive=False,
                pad={"r": 10, "t": 30},
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 900, "redraw": True},
                                "transition": {"duration": 200},
                                "fromcurrent": True
                            }
                        ]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "transition": {"duration": 0},
                                "mode": "immediate"
                            }
                        ]
                    )
                ]
            )
        ],
        annotations=[
            dict(
                x=0.5,
                y=-0.08,
                xref="paper",
                yref="paper",
                showarrow=False,
                text=(
                    "Blue dotted edges = preferred edges, "
                    "green edges = matched edges, "
                    "orange sellers = constricted sellers"
                )
            )
        ]
    )

    return fig