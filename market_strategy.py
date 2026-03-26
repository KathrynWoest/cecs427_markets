## NOTE: this file reuses a lot of code from Projects 1, 2, and 3

import sys
import file_i as fi
#import plot
#import interactive as inact
import analysis


def main():
    # get arguments from command line
    args = sys.argv
    end = len(args)

    # if there are less than 2 arguments, then not possible to do anything. terminate program.
    if end < 2:
        raise Exception(f"Program was terminated because there is no file to upload a graph with.\n---")
    
    # parse in graph from given .gml file
    user_graph = fi.parse_graph(args[1])

    # calculate preference-seller graph and conduct analysis
    round_results = analysis.analysis(user_graph)

    # call the plotting function
    #if "--plot" in args:
        #plot.plot(user_graph)

    # call the interactive display function
    #if "--interactive" in args:
        #inact.interactive(user_graph, round_results)

main()