# CECS 427 Project 4: Market and Strategic Interaction in Network
Completed By: Kathryn Woest (030131541) and Grace Flores (030169163)


## Usage Instructions
**NOTE:** `plot.py` and `interactive.py` rely on a command that is not compatible with WSL. This command automatically opens up the graph's visualization. If you are unable to use a different terminal like Powershell, comment out `plot.py`'s line 145 and `interactive.py`'s line 363 and instead manually open the generated `.html` files through your file explorer.

1. Clone this repo and open it on your IDE

2. DEPENDENCIES: This program relies on two external libraries. To install them, ensure you are inside the project directory and run these commands:
    1. **NetworkX**, a library that provides `.gml` file parsing and writing, graph support, and analysis functions. To install, run: `pip install networkx[default]`
    2. **Plotly**, a library used for creating and plotting graphs. To install, run: `pip install plotly`

3. Run this program with: `python market_strategy.py input_file.gml --plot --interactive`
    1. `market_strategy.py` and the input file must be the first and second arguments, respectively. `--plot` and `--interactive` may be provided in any order after the input file is listed.
    2. `--plot` and `--interactive` are the only optional arguments. You may choose whether to plot the original graph or to see an interactive demonstration of the market analysis, but you must provide the graph itself and `market_strategy.py`, or otherwise the program will terminate.


## Implementation Description
1. **Overall Program:** Modular program that takes a graph, finds the preference-seller graph and the maximum matching, and finds the perfect matching by increasing seller prices as necessary. Optionally plots the original graph and shows an interactive demonstration of the above market analysis process.
2. **MAIN - market_strategy.py:** Takes a graph and calls `analysis.py` to find the perfect matching of the graph, then optionally plots the graph or shows a demonstration of the analysis process. Conducts error checking for inputs. A lot of code is reused from projects 1, 2, and 3.
3. **file_i.py:** Reads in the bipartite graph from the given `.gml` file, checks that the graph is not empty, ensures all nodes have a `bipartite` attribute, then returns the graph to the main program for analysis. A lot of code is reused from projects 1, 2, and 3.
4. **analysis.py:** Contains four functions. `build_preference_seller()` builds the preference-seller graph by dividing up the nodes between buyers and sellers, determining the buyers valuations of each seller (value of buyer i - price of seller j), finding the maximum valuation (or valuations, if multiple are the same value), and adding edges between the buyers and their most valued seller(s). `reconstruct_path()` takes the result of the BFS-search through the graph with an augmented path and switches all the edges along the path from matched to unmatched and vice versa. `bfs_search()` starts from an unmatched buyer. On even layers, it adds all the unmatched edges to the traversal, and on odd layers, it adds all the matched edges. When the search finds a path that ends on an even layer (meaning it stops on an unmatched node), it calls `reconstruct_path()` as an augmented path was found. Finally, `analysis()` calls the appropriate functions to loop through, until perfect matching is found, building the preference-seller graph, finding an augmenting path and increasing the matching until maximum matching is found, and increasing the prices of the sellers in the constricted set. It then prints the results. It also returns a list of all of the preference-seller graphs with the maximum matches before they increased prices, ending with the perfect matching graph.
5. **plot.py:** Takes the bipartite market graph and creates a visualization of it, including all of its attributes. The graph is rendered into a file called `market_graph.gml`.
6. **interactive.py:** Contains 3 functions. `interactive()` is the main function which builds an animated figure of each round of the market process using plotly. The output file is named `market_graph_interactive.html`. `_get_groups()` is a helper function used in `interactive()` to identify the buyer and seller groups from the graph, since that information is not expilictly stored in the `.gml` file. Sellers are identified as nodes with a "price" attribute,
while buyers are those without one. `_find_constricted_sellers()` is another helper function that is used to recompute the constricted set to use in the interactive figure. Starting from an unmatched buyer, this performs a BFS using the alternating path rules (unmatched edges followed by matched edges). If no augmenting path is found, then the visited sellers correspond to the constricted set.


## Example Command and Output
Note: only one sample is provided, as we only received one test input `.gml` file and there are no other variable inputs.
1. Command: `python3 market_strategy.py market.gml --plot --interactive`

Outputs are annotated in this PDF: https://pdflink.to/75874a19/
