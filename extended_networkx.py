import networkx as nx
import random
from typing import Set, Any, List


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


def all_neighbors(G: nx.DiGraph, n) -> Set[Any]:
    """
    Returns a set of successors and predecessors of node n in G.
    """
    return set(list(G.successors(n)) + list(G.predecessors(n)))


def connected_random_subgraph(G: nx.Graph, n: int) -> nx.Graph:
    """
    Samples n nodes from a connected component of G which are also connected.
    """
    # list of connected components with more than n nodes
    components = [g for g in nx.weakly_connected_components(G) if len(g) > n]
    print(f"There are {len(components)} components with more than {n} nodes.")
    random_component: Set = random.choice(list(components))
    start_node = random.choice(list(random_component))
    selected_nodes: List[Any] = [start_node]
    candidate_nodes: Set[Any] = all_neighbors(G, start_node)
    while len(selected_nodes) < n:
        if len(candidate_nodes) == 0:
            break
        if len(candidate_nodes) > 0:
            selected_candidate = random.choice(list(candidate_nodes))
        else:
            selected_candidate = candidate_nodes.pop()
        # Remove the newly selected node from candidates
        candidate_nodes.remove(selected_candidate)
        # Add the newly selected node to selected nodes
        selected_nodes.append(selected_candidate)
        # Add the newly selected node's neighbors to candidates (without already selected nodes)
        candidate_nodes.update(all_neighbors(G, selected_candidate) - set(selected_nodes))
    return nx.subgraph(G, selected_nodes)
