import networkx as nx
import random
import scipy
from typing import Set, Any, List
import igraph
import random
import collections


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
    A = nx.adjacency_matrix(G).tolil()  # adjacency matrix converted into list of lists
    # Run floyd-warshall algorithm to find shortest paths
    D = scipy.sparse.csgraph.floyd_warshall(A, directed=True, unweighted=False)

    n = D.shape[0]  # Number of nodes
    centralities = {}
    for node_index in range(0, n):
        cc = 0.0
        possible_paths = D[node_index, :]
        shortest_paths = list(filter(lambda x: x != float("inf"), possible_paths))

        total = sum(shortest_paths)
        n_shortest_paths = len(shortest_paths) - 1
        if total > 0.0 and n > 1:
            s = n_shortest_paths / (n - 1)
            cc = (n_shortest_paths / total) * s
        centralities[node_index] = cc
    return centralities

def longest_path(G):
    shortest_paths_lengths = dict(nx.all_pairs_shortest_path_length(G))
    max = 0
    for source in shortest_paths_lengths.keys():
        for target in shortest_paths_lengths[source].keys():
            if shortest_paths_lengths[source][target] > max:
                max = shortest_paths_lengths[source][target]
    return max
  

def exclusive_neighborhood(G, v, Vp):
    assert type(G)==igraph.Graph
    assert type(v)==int
    assert type(Vp)==set
    Nv = set(G.neighborhood(v))
    NVpll = G.neighborhood(list(Vp))
    NVp = set([u for sublist in NVpll for u in sublist])
    return Nv - NVp

def extend_subgraph(G, Vsubgraph, Vextension, v, k, k_subgraphs):
    assert type(G)==igraph.Graph
    assert type(Vsubgraph)==set
    assert type(Vextension)==set
    assert type(v)==int
    assert type(k)==int
    assert type(k_subgraphs)==list
    if len(Vsubgraph) == k:
        k_subgraphs.append(Vsubgraph)
        assert 1==len(set(G.subgraph(Vsubgraph).clusters(mode=igraph.WEAK).membership))
        return
    while len(Vextension) > 0:
        w = random.choice(tuple(Vextension))
        Vextension.remove(w)
        ## obtain the "exclusive neighborhood" Nexcl(w, vsubgraph)
        NexclwVsubgraph = exclusive_neighborhood(G, w, Vsubgraph)
        VpExtension = Vextension | set([u for u in NexclwVsubgraph if u > v])
        extend_subgraph(G, Vsubgraph | set([w]), VpExtension, v, k, k_subgraphs)
    return

def enumerate_subgraphs(G, k):
    assert type(G)==igraph.Graph
    assert type(k)==int
    k_subgraphs = []
    for vertex_obj in G.vs:
        v = vertex_obj.index
        Vextension = set([u for u in G.neighbors(v) if u > v])
        extend_subgraph(G, set([v]), Vextension, v, k, k_subgraphs)
    return k_subgraphs

