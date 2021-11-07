
import networkx as nx

def load_graph(filename : str = "out_graph.gml"):
    return nx.read_gml(filename)

def capitalization_attribute(G):
    """
    Adds the 'capitalization' attribute to every node, which is the sum of the incoming edges weighs.
    """
    for node in G.nodes():
        capitalization = 0
        for edge in G.in_edges(node):
            capitalization += G.get_edge_data(*edge)["weight"]
        G.nodes[node]["capitalization"] = capitalization

def max_k_capitalization(G, k:int=10):
    """
    Finds the top k nodes with the highest capitalization.
    """
    return sorted(G.nodes(), key=lambda n: G.nodes[n]["capitalization"], reverse=True)[:k]

def k_core(G, k):
    return nx.k_core(G, k)

def betweenness_centrality(G, percentage : float = 0.1, normalized:bool = True):
    n = G.number_of_nodes()
    k = int(n * percentage)
    print(f"Computing approximate betweenness centrality for {k} nodes out of {n}")
    return nx.betweenness_centrality(G, k=k, normalized=normalized, weight="weight")

def closeness_centrality(G):
    pass # Networkx does not have approximate algorithm

def clustering_coefficient(G):
    return nx.clustering(G, weight="weight")



def main():
    print("Loading graph")
    G = load_graph()
    capitalization_attribute(G)
    print("Graph loaded:\n", G)
    k = 20
    print(f"Top {k} nodes with highest capitalization: {max_k_capitalization(G, k)}")
    b_centralities = betweenness_centrality(G, percentage=0.02)
    print(sorted(b_centralities.items(), key=lambda t: t[1], reverse=True)[:20])
    #clustering_coeff = clustering_coefficient(G)
    #print(sorted(clustering_coeff.items(), key=lambda t: t[1], reverse=True)[:20])

if __name__ == "__main__":
    main()