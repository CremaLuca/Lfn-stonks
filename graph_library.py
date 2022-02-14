import networkx as nx
import random
import scipy
from typing import Set, Any, List
import igraph


__author__ = "Luca Crema, Riccardo Crociani"
__version__ = "0.2"
__all__ = ["max_k_nodes", "betweenness_centrality_percent", "all_neighbors", "connected_random_subgraph"]


def max_k_nodes(G: nx.Graph, k: int, attribute: str) -> List[Any]:
    """
    Finds the k nodes with the highest value of the given attribute.
    """
    return sorted(G.nodes(), key=lambda x: G.nodes[x][attribute], reverse=True)[:k]


def betweenness_centrality_percent(G: nx.Graph, percentage: float = 0.1, normalized: bool = True) -> dict:
    """
    Computes the approximated betweenness centrality using a given percentage of nodes.
    """
    if percentage < 0.0 or percentage > 1.0:
        raise ValueError("Percentage must be between 0.0 and 1.0.")
    n = G.number_of_nodes()
    k = int(n * percentage)
    return nx.betweenness_centrality(G, k=k, normalized=normalized, weight="weight")


def all_neighbors(G: nx.DiGraph, n) -> Set[Any]:
    """
    Returns a set of successors and predecessors of node n in the DiGraph G.
    """
    return set(list(G.successors(n)) + list(G.predecessors(n)))


def connected_random_subgraph(G: nx.Graph, n: int) -> nx.Graph:
    """
    Samples n connected vertices from a connected component of G.
    """
    # List of connected components with more than n nodes
    components = [g for g in nx.weakly_connected_components(G) if len(g) > n]
    print(f"There are {len(components)} components with more than {n} nodes.")
    if len(components) == 0:
        raise ValueError(f"There are no connected components with more than {n=} nodes.")
    # Sample one of the random components
    random_component: Set = random.choice(list(components))
    # Sample a random node
    start_node = random.choice(list(random_component))
    # Initialize selected and candidate nodes
    selected_nodes: List[Any] = [start_node]
    candidate_nodes: Set[Any] = all_neighbors(G, start_node)
    while len(selected_nodes) < n and len(candidate_nodes) > 0:
        if len(candidate_nodes) == 1:
            selected_candidate = candidate_nodes.pop()
        else:
            selected_candidate = random.choice(list(candidate_nodes))
            # Remove the newly selected node from candidates
            candidate_nodes.remove(selected_candidate)
        # Add the newly selected node to selected nodes
        selected_nodes.append(selected_candidate)
        # Add the newly selected node's neighbors to candidates (without already selected nodes)
        candidate_nodes.update(all_neighbors(G, selected_candidate) - set(selected_nodes))
    return nx.subgraph(G, selected_nodes)


def closeness_centrality_matrix(G):
    """
    Returns the closeness centrality of all the nodes of G.
    """
    A = nx.adjacency_matrix(G).tolil()  # adjacency matrix converted into list of lists
    # Run floyd-warshall algorithm to find shortest paths
    D = scipy.sparse.csgraph.floyd_warshall(A, directed=True, unweighted=False)
    node_list = list(G.nodes())
    centralities = {}
    n = D.shape[0]  # Number of nodes
    for node_index in range(0, n):
        cc = 0.0
        possible_paths = D[node_index, :]
        shortest_paths = list(filter(lambda x: x != float("inf"), possible_paths))

        total = sum(shortest_paths)
        n_shortest_paths = len(shortest_paths) - 1
        if total > 0.0 and n > 1:
            s = n_shortest_paths / (n - 1)
            cc = (n_shortest_paths / total) * s
        centralities[node_list[node_index]] = cc
    return centralities


def max_out_degree_vertex(G: nx.DiGraph):
    """
    Returns the vertex with the maximum out-degree in G.
    """
    return max(G.nodes(), key=lambda x: G.out_degree(x))


def max_in_degree_vertex(G: nx.DiGraph):
    """
    Returns the vertex with the maximum in-degree in G.
    """
    return max(G.nodes(), key=lambda x: G.in_degree(x))


def min_in_degree_vertex(G: nx.DiGraph):
    """
    Returns the vertex with the minimum in-degree in G.
    """
    return min(G.nodes(), key=lambda x: G.in_degree(x))


def longest_path(G) -> List[str]:
    """
    Returns the longest path of G.
    """
    shortest_paths = dict(nx.all_pairs_shortest_path(G))
    max_len = 0
    max_path = None
    for source in shortest_paths.keys():
        for target in shortest_paths[source].keys():
            if len(shortest_paths[source][target]) > max_len:
                max_len = len(shortest_paths[source][target])
                max_path = shortest_paths[source][target]
    return max_path


def exclusive_neighborhood(G: igraph.Graph, v: int, Vp: set):
    """
    Used by ESU algorithm.
    Returns the set of neighbors that are not already neighbors of any node in Vp.
    """
    Nv = set(G.neighborhood(v, mode="out"))
    NVpll = G.neighborhood(list(Vp), mode="out")
    NVp = {u for sublist in NVpll for u in sublist}
    return Nv - NVp


def extend_subgraph(G: igraph.Graph, Vsubgraph: set, Vextension: set, v: int, k: int, k_subgraphs: list):
    """
    Used by ESU algorithm.
    Updates Vextension and k_subgraphs.
    """
    if len(Vsubgraph) == k:
        k_subgraphs.append(Vsubgraph)
        assert 1 == len(set(G.subgraph(Vsubgraph).clusters(mode=igraph.WEAK).membership))
        return
    while len(Vextension) > 0:
        w = random.choice(tuple(Vextension))
        Vextension.remove(w)
        # obtain the "exclusive neighborhood" Nexcl(w, vsubgraph)
        NexclwVsubgraph = exclusive_neighborhood(G, w, Vsubgraph)
        VpExtension = Vextension | {u for u in NexclwVsubgraph if u > v}
        extend_subgraph(G, Vsubgraph | {w}, VpExtension, v, k, k_subgraphs)
    return


def enumerate_subgraphs(G: igraph.Graph, k: int):
    """
    Returns a list of set objects containing the vertices of each of the size k subgraphs
    """
    k_subgraphs: list = []
    for vertex_obj in G.vs:
        v = vertex_obj.index
        Vextension = {u for u in G.neighbors(v, mode="out") if u > v}
        extend_subgraph(G, {v}, Vextension, v, k, k_subgraphs)
    return k_subgraphs
