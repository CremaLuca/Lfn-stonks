# Learning from networks project documentation

**Partecipants**:

- Luca Crema 2026827
- Riccardo Crociani 2022466

## Title

How hard is it to work on a new raw dataset? Which **useful** metrics can be computed in reasonable time?

## Motivation

We want to explore the process of data gathering, convert them to a graph and compute meaningful metrics on it.

## Data

Exchanged Traded Funds (ETFs) components datasets.

An ETF is an asset traded on the stock market just like any other stock that usually tracks a stock index.
The ETF's "underlying" components are the same as the tracked index's component and are bought in the same percentage as defined in the index.
An ETF is emitted and sold by an "Authorized Partecipant" which is in charge of making sure the ETF is following the index as closely as possible.

### Where to find it

Start from an initial dataset found for free [at this link](https://masterdatareports.com/), which is updated at around the end of each month.

### What kind of graph

It is a weighted directed graph. The nodes can represent fund nodes or component nodes, note that a fund node can also be a component. Edges go from a fund node to a component node and the weight is the amount of money in euros the fund owns of that component.

### Number of nodes and edges

The american and european financial market contains about 100.000 securities between stocks, bonds and funds, so we expect that order of magnitude for the nodes (the initial dataset contains 31.000 nodes). Each fund contains on average a few hundred components so we are expecting an order of magnitude of a milion edges (the initial dataset contains 420.000 edges).

## Method

The method we are going to use to parse the gathered data into a graph is by trial and error: each raw dataset has its own types of errors so all we can do is explore each dataset individually.

### Computational problem

Once the datasets are clean and parsed, we want to apply some of the different metrics computation algorithms we have seen, exploring the limits of the exact computations and the reachable levels of approximation.

## Algorithms

Some of the node-level metrics, network patterns and network clustering algorithms.
- ### In-degree(v) and out-degree(v):
    Representing respectively the number of funds buying node v and the number of components bought by fund v
- ### Longest path:
    Representing the number of funds buying other funds
- ### Approximated betweennes centrality:
    Since the graph is too large to compute the exact betweenness centrality of each node, we use betweenness_centrality_percent(G, percentage=0.02) from our extended library to compute an approximation on a small percentage of the nodes. It measures how central is a node in the graph. Clearly the largest centrality is given by the fund nodes since components nodes can not have out edges.

- ### Closeness centrality:
    It measures how central is a node with respect to all the others in the graph. 

- ### Clustering coefficient:
    Can be computed exactly. In this case a triangle represent a fund bought by another fund, and both buying the same component

- Embedding using node2vec approach

- ESU algorithm: 





## Implementations/libraries

We are mostly going to use python code with networkx library for graph analysis and pandas with numpy to parse the dataset.

#### Experiments

We are interested in computing the various graph scores on a "unexplored" dataset and give them a meaning.

### Machine for experiments

The machines used are: 
- Xiaomi with 4.3GHz 4-core Intel i5 CPU, 16GB RAM DDR3 1600Hz, 30GB free SSD space, 500GB free HDD space, 2GHz Nvidia GTX1050Ti GPU.
- MacBook Pro with Chip Apple M1 Pro, 16 GB RAM, CPU 8‑core with 6 performance core and 2 efficiency core, GPU 14‑core,Neural Engine 16‑core, 


## References

- [Master data reports initial dataset](https://masterdatareports.com/)
- [Networkx library](https://networkx.org/)
- [Karate Club unsupervised learning library](https://github.com/benedekrozemberczki/karateclub)
- [Pandas library](https://pandas.pydata.org/)
- [Numpy library](https://numpy.org/)
- [Scipy library](https://scipy.org/)
- [Official python wiki: Graph computation resources](https://wiki.python.org/moin/PythonGraphApi)
- [Igraph library](https://igraph.org)