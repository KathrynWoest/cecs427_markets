import networkx as nx
import copy


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
        if price is not None:
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
    
    try:
        # begin constructing the preference-seller graph by adding all the nodes to the new graph
        pref_sell = nx.Graph()
        pref_sell.add_nodes_from(graph.nodes(data=True))
        
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
            
        # initialize all nodes and edges to not be matched
        for node in pref_sell.nodes:
            pref_sell.nodes[node]["matched"] = False

        for u, v in pref_sell.edges:
            pref_sell.edges[u, v]["matched"] = False

    except Exception as e:
        raise Exception("Program terminated due to an error in constructing the preference-seller graph. Error:", e)

    # return the preference-seller graph, buyers, and sellers
    return pref_sell, buyers, sellers


def reconstruct_path(ps_graph, parents, end):
    """Function that takes a BFS-search and reconstructs the augmented path
    Inputs: the dict that stores all the traversed nodes and their parents and the ending unmatched node to end the augmented path on
    Returns: N/A"""
    
    try:
        path = []
        # while we haven't found the original unmatched node (the buyer)
        while end is not None:
            # add the current node, and load its parent
            path.append(end)
            end = parents[end]
        
        path.reverse()

        # iterate through the augmented path, switching the matched/unmatched edges
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            if ps_graph.edges[edge].get("matched"):
                ps_graph.edges[edge]["matched"] = False
            else:
                ps_graph.edges[edge]["matched"] = True
        
        # now reset all the nodes too
        for node in ps_graph.nodes():
            ps_graph.nodes[node]["matched"] = False
        
        for u, v in ps_graph.edges():
            if ps_graph.edges[(u, v)].get("matched"):
                ps_graph.nodes[u]["matched"] = True
                ps_graph.nodes[v]["matched"] = True

    except Exception as e:
        raise Exception("Program terminated because the augmented path was unable to be applied. Error:", e)


def bfs_search(ps_graph, starter, sellers):
    """Function that conducts the BFS-search (using the 'unmatched edges -> matched edge' pattern we learned in class)
    Inputs: the preference-seller graph and an unmatched buyer to start the search
    Returns: EITHER 'False to indicate no path found and the visited nodes' OR 'True to indicate path found and None (no visited nodes need to be tracked)'"""

    # initialize the BFS search, the list of visited nodes, the iterator, and the dictionary to keep track of parents
    bfs_path = [[starter]]
    visited = [starter]
    parent_tracker = {starter: None}
    iterator = 0
    
    try:
        # we know that the number of BFS layers will never be longer than the number of nodes, so set that to be the guaranteed cut-off
        while iterator < len(ps_graph.nodes()):
            # even step, add ALL edges not visited yet
            if iterator % 2 == 0:
                next = []
                # for each node in the layer before the one we are currently constructing, find ALL their edges
                for next_node in bfs_path[iterator]:
                    edges = ps_graph.edges(next_node)
                    for u, v in edges:
                        if u != next_node:
                            other = u
                        else:
                            other = v
                        # if the node the edge is connecting to hasn't been visited, add to the traversal
                        if not ps_graph.edges[(u, v)].get("matched", False) and other not in visited:
                            next.append(other)
                            visited.append(other)
                            parent_tracker[other] = next_node

                            # we are on an even layer. if we find a non-matched node at this point, it indicates an augmented path
                            # call `reconstruct_path()` to find and return the augmented path
                            if other in sellers and not ps_graph.nodes[other].get("matched", False):
                                reconstruct_path(ps_graph, parent_tracker, other)
                                return True, None
                
                # if we actually added new nodes to this layer, then add them and iterate to the next layer
                if len(next) > 0:
                    bfs_path.append(next)
                    iterator += 1
                # otherwise, break early and finish function
                else:
                    break

            # odd step, add matched edge not visited yet
            else:
                next = []
                # for each node in the layer before the one we are currently constructing, find their matched edges
                for next_node in bfs_path[iterator]:
                    edges = ps_graph.edges(next_node)
                    for u, v in edges:
                        if u != next_node:
                            other = u
                        else:
                            other = v
                        # if the node the edge is connecting to hasn't been visited and is the matching edge, add to the traversal
                        if ps_graph.edges[(u, v)].get("matched", False) and other not in visited:
                            next.append(other)
                            visited.append(other)
                            parent_tracker[other] = next_node

                # if we actually added new nodes to this layer, then add them and iterate to the next layer      
                if len(next) > 0:
                    bfs_path.append(next)
                    iterator += 1
                # otherwise, break early and finish function
                else:
                    break

    except Exception as e:
        raise Exception("Program terminated because something went wrong while searching for an augmented path. Error:", e)

    # return false to indicate no augmented path was found and that prices should be increased in the sellers
    return False, visited   


def analysis(graph):
    """Function that controls the overall logic of the perfect matching process utilizing preference-seller graphs, augmented paths, and constricted sets
    Inputs: the user graph
    Returns: printed description of the perfect matching and a dict that tracks each step of the process"""

    # as the graph will be changed throughout the process, make a copy of it for the analysis
    graph = copy.deepcopy(graph)
    perfect_matching = False
    graph_tracker = []

    try:
        while not perfect_matching:
            # build the preference-seller graph
            ps_graph, buyers, sellers = build_preference_seller(graph)
            
            # create initial matching by matching buyers with first seller they can connect to
            for buyer in buyers:
                buyer_matched = False
                edges = ps_graph.edges(buyer)
                for u, v in edges:
                    if u != buyer:
                        seller = u
                    else:
                        seller = v

                    if not ps_graph.nodes[seller].get("matched", False):
                        ps_graph.nodes[seller]["matched"] = True
                        ps_graph.nodes[buyer]["matched"] = True
                        ps_graph.edges[(u, v)]["matched"] = True
                        buyer_matched = True

                    if buyer_matched:
                        break
            
            result = True
            while result:
                # check for unmatched buyers
                unmatched = False
                starter = None

                for buyer in buyers:
                    if not ps_graph.nodes[buyer].get("matched", False):
                        starter = buyer
                        unmatched = True
                        break

                # if all the buyers are matched, we found the perfect matching!
                if not unmatched:
                    perfect_matching = True
                    graph_tracker.append(copy.deepcopy(ps_graph))
                    break
                
                # else, not all matched, so determine if an augmented path exists
                result, visited = bfs_search(ps_graph, starter, sellers)
            
                # there's no augmented path, just up the prices of the constricted set sellers and repeat
                if result == False:
                    graph_tracker.append(copy.deepcopy(ps_graph))
                    for seller in sellers:
                        if seller in visited:
                            graph.nodes[seller]["price"] += 1
                    break

    except Exception as e:
        raise Exception("Program terminated because something went wrong in completing the market analysis. Error:", e)

    # print formatted results
    print("-----")
    print("Perfect matching has been found:")
    for u, v, match in ps_graph.edges(data="matched"):
        if match:
            if u in sellers:
                print(f"Seller {u} matched to buyer {v}.")
            else:
                print(f"Seller {v} matched to buyer {u}.")
    print("-----")
    
    # return a list of all the preference-seller graphs found with maximum matching
    return graph_tracker
    
