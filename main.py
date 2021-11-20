import networkx as nx
import extended_networkx as ex
import sys
import numpy as np
import scipy


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


def random_graph(n, p):

    # Returns a $G_{n,p}$ random graph, also known as an Erdős-Rényi graph or
    # a binomial graph.
    G = nx.fast_gnp_random_graph(n, p, directed=True)
    return G


# TODO: Associate the label of each node (instead of an int) with its cc
def closeness_centrality_matrix(G):
    A = nx.adjacency_matrix(G).tolil()  # matrix converted into list of lists
    D = scipy.sparse.csgraph.floyd_warshall(A, directed=False, unweighted=False)

    n = D.shape[0]
    centralities = {}
    for r in range(0, n):

        cc = 0.0

        possible_paths = list(enumerate(D[r, :]))
        shortest_paths = dict(filter(lambda x: not x[1] == np.inf, possible_paths))

        total = sum(shortest_paths.values())
        n_shortest_paths = len(shortest_paths) - 1.0
        if total > 0.0 and n > 1:
            s = n_shortest_paths / (n - 1)
            cc = (n_shortest_paths / total) * s
        centralities[r] = cc
    return centralities


def clustering_coefficient(G):
    return nx.clustering(G, weight="weight")


def main():
    print("Loading graph")
    G = load_graph(sys.argv[1])
    compute_capitalization(G)
    print("Graph loaded:\n", G)
    k = 20

    print("-----------------------------------------------")
    print(f"Top {k} nodes with highest capitalization: {ex.max_k_nodes(G, k, 'capitalization')}")
    print("-----------------------------------------------")

    b_centralities = ex.betweenness_centrality_percent(G, percentage=0.02)
    print(sorted(b_centralities.items(), key=lambda t: t[1], reverse=True)[:k])

    print("-----------------------------------------------")
    print("Clustering coefficient")
    print("-----------------------------------------------")
    clustering_coeff = clustering_coefficient(G)
    print(sorted(clustering_coeff.items(), key=lambda t: t[1], reverse=True)[:k])
    print("-----------------------------------------------")

    print("Closensess centrality (matrix method)")
    c_centralities = closeness_centrality_matrix(random_subgraph(G, int(0.1 * G.number_of_nodes())))
    print(sorted(c_centralities.items(), key=lambda t: t[1], reverse=True)[:k])


if __name__ == "__main__":
    main()
