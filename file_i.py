## NOTE: this file reuses a lot of code from Projects 1, 2, and 3

import networkx as nx

def parse_graph(file_name):
    """Takes the input file and parses it into a NetworkX graph that can be analyzed. Checks for empty graphs and for edges with no bipartite values.
    Input: .gml file name of the submitted graph
    Output: NetworkX graph of the submitted graph from the file"""
    
    if ".gml" not in file_name:
        raise Exception("Input file type is not .gml, so program terminated. Provided file:", file_name)

    try:
        # reads .gml file and parses it into the graph
        submitted_graph = nx.read_gml(file_name)

        # check if the graph is empty
        if submitted_graph.number_of_nodes == 0 or submitted_graph.number_of_edges == 0:
            raise Exception("Program terminated because the graph has no nodes and/or no edges.")
        
        # check if any of the nodes don't have bipartite value
        for node, bi in submitted_graph.nodes(data="bipartite"):
            if bi == None:
                raise Exception(f"Program terminated because node '{node}' doesn't have a bipartite attribute.")
        
        return submitted_graph
    
    except Exception as e:
        raise Exception("Program quit due to an error in reading and parsing the graph from the provided .gml file. Provided error:", e)
    