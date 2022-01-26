import networkx as nx

# import extended_networkx as ex
import sys
import numpy as np


def load_graph(filename: str = "out_graph.gml"):
    return nx.read_gml(filename)


def compute_capitalization(G):
    """
    Adds the 'capitalization' attribute to every node, which is the sum of the incoming edges weighs.
    """
    for node in G.nodes():
        capitalization = 0
        for edge in G.in_edges(node):
            capitalization += G.get_edge_data(*edge)["weight"]
        G.nodes[node]["capitalization"] = capitalization


def random_subgraph(G, n_nodes):
    """ """
    # Returns a random subgraph of G with n_nodes nodes and no negative cycles

    sub_graph = nx.subgraph(G, list(np.random.choice(list(G.nodes), n_nodes, replace=False)))
    while nx.negative_edge_cycle(nx.Graph(sub_graph)):
        sub_graph = nx.subgraph(G, list(np.random.choice(list(G.nodes), n_nodes, replace=False)))
    return sub_graph


def main():
    print("Loading graph")
    G = load_graph(sys.argv[1])
    compute_capitalization(G)
    print("Graph loaded:\n", G)


if __name__ == "__main__":
    main()
