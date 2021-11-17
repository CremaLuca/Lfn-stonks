import networkx as nx
import extended_networkx as ex


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


def closeness_centrality(G):
    pass  # Networkx does not have approximate algorithm


def main():
    print("Loading graph")
    G = load_graph()
    compute_capitalization(G)
    print("Graph loaded:\n", G)
    k = 20
    print(f"Top {k} nodes with highest capitalization: {ex.max_k_nodes(G, k, 'capitalization')}")
    b_centralities = ex.betweenness_centrality_percent(G, percentage=0.02)
    print(sorted(b_centralities.items(), key=lambda t: t[1], reverse=True)[:20])
    # clustering_coeff = clustering_coefficient(G)
    # print(sorted(clustering_coeff.items(), key=lambda t: t[1], reverse=True)[:20])


if __name__ == "__main__":
    main()
