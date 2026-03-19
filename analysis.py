import networkx as nx


def build_preference_seller(graph):
    """Function that builds the preference-seller graph based on the input graph
    Input: graph with buyer/seller nodes, seller prices, and buyer valuations
    Output: the constructed preference-seller graph"""

    sellers = []
    buyers = []
    seller_group = ""
    buyer_group = ""
    sell = False
    buy = False

    # determine what values are used to distinguish buyers and sellers
    for node, price in graph.nodes(data="price"):
        if price != None:
            seller_group = graph.nodes[node]["bipartite"]
            sell = True
        else:
            buyer_group = graph.nodes[node]["bipartite"]
            buy = True
        if sell and buy:
            break
    
    # create lists of the buyers and sellers, and raise an error if a node exists that is not a buyer or seller
    for node, bi in graph.nodes(data="bipartite"):
        if bi == seller_group:
            sellers.append(node)
        elif bi == buyer_group:
            buyers.append(node)
        else:
            raise Exception(f"Program terminated because market analysis is unable to be calculated. Node '{node}' is not classified as a buyer or seller.")
    
    # ensure the graph is bipartite 
    if len(sellers) != len(buyers):
        raise Exception(f"Program terminated because market analysis is unable to be calculated. There are more buyers than sellers or vice versa.")
    
    # begin constructing the preference-seller graph by adding all the nodes to the new graph
    pref_sell = nx.Graph()
    pref_sell.add_nodes_from(graph.nodes)
    
    # go through each buyer and determine what they value every seller's node at (value - price)
    for node in buyers:
        node_values = {}

        # find all the buyer's edges and add what they value the seller at to a dict, using the seller as the key
        linked_edges = graph.edges(node)
        for u, v in linked_edges:
            if u != node:
                seller = u
            else:
                seller = v
            val = graph.edges[(u, v)]["valuation"] - graph.nodes[seller]["price"]
            node_values[seller] = val

        # determine which seller(s) they value the highest, and add the edge(s) to the preference-seller graph
        max_value = max(node_values.values())
        for k, v in node_values.items():
            if v == max_value:
                pref_sell.add_edge(k, node)

    # return the preference-seller graph
    return pref_sell

def analysis(graph):
    ps_graph = build_preference_seller(graph)
    
