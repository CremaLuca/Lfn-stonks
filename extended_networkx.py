import networkx as nx


def max_k_nodes(G: nx.Graph, k: int, attribute: str):
    """
    Finds the k nodes with the highest value of the given attribute.
    """
    return sorted(G.nodes(), key=lambda x: G.nodes[x][attribute], reverse=True)[:k]


def betweenness_centrality_percent(G: nx.Graph, percentage: float = 0.1, normalized: bool = True):
    """
    Computes the approximated betweenness centrality using the given percentage of nodes.
    """
    n = G.number_of_nodes()
    k = int(n * percentage)
    return nx.betweenness_centrality(G, k=k, normalized=normalized, weight="weight")
