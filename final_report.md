# Learning from networks project documentation

- Luca Crema 2026827
- Riccardo Crociani 2022466

## Title

How hard is it to work on a new raw dataset? Which **useful** metrics can be computed in reasonable time?

## Motivation

We want to explore the process of **data gathering**, **convert** them **to a graph** and **compute meaningful metrics** on it.

## Content

The content of the project is entirely browsable on the [GitHub repository](https://github.com/CremaLuca/Lfn-stonks) where you can find the following:

- The [README](https://github.com/CremaLuca/Lfn-stonks/README.md) with instructions on how to run the project.
- The Jupyter [notebook.ipynb](https://github.com/CremaLuca/Lfn-stonks/notebook.ipynb) with the (already executed) code.
- **This report** file source: [final_report.md](https://github.com/CremaLuca/Lfn-stonks/final_report.md).
- The libraries [csv_to_graph.py](https://github.com/CremaLuca/Lfn-stonks/csv_to_graph.py) and [graph_library.py](https://github.com/CremaLuca/Lfn-stonks/graph_library.py) used in the notebook.

NOTE: you can view the project with the VSCode interface on your browser at [this link](https://github.dev/CremaLuca/Lfn-stonks)

## Data

Exchanged Traded Funds (ETFs or "funds") components datasets.

An ETF is an asset traded on the stock market just like any other stock that usually tracks a stock index.
The ETF's "underlying" components are the same as the tracked index's component and are bought in the same percentage as defined in the index.
An ETF is emitted and sold by an "Authorized Partecipant" which is in charge of making sure the ETF is following the index as closely as possible.

### Where to find it

The dataset we used can be found for free [at this link](https://masterdatareports.com/Download-Files/ConstituentData42.csv).

### What kind of graph

We want to produce a weighted directed graph. The nodes can represent an ETF/fund or a component, note that a fund node can also be a component to another fund. Edges go from a fund node to a component node and the weight is the amount of money in euros the fund owns of that component.

### Number of nodes and edges

We were able to extract around `25000` nodes and `396000` edges from the dataset which is only a constant factor away from the sizes we expected in the project proposal.
We have about `1500` ETF nodes and `21000` components, where an ETF has `250` components on average and a component is part of `18` ETFs on average.

## Method

The method we used to parse the gathered data into a graph is mostly based on trial and error but although each dataset has its own types of errors we applied standard data cleaning techniques.
Later we tried to analised the parsed graph to extract some of the metrics looking for unexpected values.

### Data cleaning

An initial error detection method is to manually check the data and see if there are any unexpected values, but being the dataset of `856000` rows this is not feasible. So we started by applying simple standard data cleaning methods, but this lead to dropping too many rows. At the end we had to tailor-make our cleaning methods with **a lot** of trial and error.
The result is a pipeline of around 9 steps that are:

- Drop rows with missing "market value" values
- Drop duplicate rows
- Fill empty currency values with "USD" (which is a strong assumption, but we would have lost too many rows otherwise)
- Remove ticker locations (.MI, .JP, .NQ) from ticker names
- Removing "CASH_" from ticker names that cleary represent currencies
- Replacing "0" tickers with the currency value
- Filling missing ticker values with ticker values from other rows with the same ISIN (ISIN and Ticker are both identifier of a stock, although ISIN is unique in the world and ticker is unique for the single exchange)
- Drop rows with invalid ticker values using regex
- Converting all currencies to EUR

At the end of the pipeline we are able to preserve `396000` of the `856000` lines.

The pipeline was then generalized to accept parameters, so the `csv_to_graph.py` can parse datasets from the same source even if they were to change or the project requirements change.

### Graph parsing

The cleaned pandas datatable is parsed into a directed graph using the `networkx.from_pandas_edgelist` function, using the `weight` column as the edge weight.
The best format to store the graph in a file is a `.gml` file, as it is used by visualization programs (Gephi) and supports weights on edges (unlike plain edge list).

### Graph analysis

Once the dataset is clean and parsed to graph, we applied some of the node-level metrics, network patterns, network clustering algorithms, and node embeddings, exploring the limits of the exact computations and the reachable levels of approximation.

- #### In-degree(v) and out-degree(v)

    They represent respectively the number of funds buying node v and the number of components bought by fund v.

- #### Longest path

    Represents the length of the chain of funds buying other funds.

- #### Betweennes centrality (approximated)

    It measures how central is a node in the graph by means of shortest paths. This measure shouldn't convey much information as all the paths are short and the graph is sparsely connected.
    Since the graph is too large to compute the exact betweenness centrality of each node, we use `ex.betweenness_centrality_percent(G, percentage=p)` to compute an approximation on a small percentage of the nodes such that the computation takes reasonable time (few minutes).

- #### Closeness centrality

    It measures how close is a node to all the other nodes in the graph.
    Although this metric shouldn't convey intresting information, like betweenness centrality, we computed it twice. The first is an exact method using Floyd-Warshall algorithm with adjacency matrix which is much more efficient then standard networkx's and runs in reasonable time.
    The second is also an exact algorithm from networkx, but it runs on a randomly connected subgraph generated by the method `ex.connected_random_subgraph(G: nx.Graph, n: int)` we devised.

- #### Clustering coefficient

    Although the graph is very large the clustering coefficient can be computed exactly because a triangle is a very rare occurrency.
    In this case a triangle represent a fund bought by another fund, and both buying the same component.
    Computation is done using the networkx algorithm `nx.clustering(G, weight="weight")`.

- #### Embedding using node2vec approach

    A quick way to get an idea of the graph structure are two dimensional embeddings.
    We used a python implementation of node2vec to embed the graph in a two dimension space and visulize it using the matplotlib library.

- #### ESU algorithm

    Since the graph is very large the computation of all the subgraphs of size k, for k=1,2,3,4 takes too long.
    In our case the enumeration of all the graphlets doesn't convey relevant information because we already have an idea of what are the frequencies of small patterns in the graph.

## Results

The answer to the question "is it hard to clean, parse and analyze new datasets?" is, as expected, **yes it is**. Most of the difficulty comes from the unexpected errors that can be found in a dirty dataset, which are not predictable or cannot always be spotted.
The standard cleaning methods we adopted were only partially helpful, as they have to be adapted to the specific problem and do not always improve the data quality. It was very difficult to balance filtering (removing wrong rows) with fixing (interpolation or copying missing attributes from other rows), the former leading to a greater loss of data and the latter leading to errors and inconsistencies.
Another critical part of the project was finding, devising and adapting existing algorithms because most of what we found in libraries were exact algorithms with infeasible computation times for our graph.

## References

- [Master data reports initial dataset](https://masterdatareports.com/)
- [Networkx library](https://networkx.org/)
- [Pandas library](https://pandas.pydata.org/)
- [Numpy library](https://numpy.org/)
- [Scipy library](https://scipy.org/)
- [Official python wiki: Graph computation resources](https://wiki.python.org/moin/PythonGraphApi)
- [Igraph library](https://igraph.org)
- [Node2vec implementation](https://github.com/eliorc/node2vec)
- [Closeness centrality Floyd-Warshall implementation](https://medium.com/@pasdan/closeness-centrality-via-networkx-is-taking-too-long-1a58e648f5ce)
- [ESU algorithm implementation](https://notebook.community/ramseylab/networkscompbio/class18_motifs_python3_template)

## Contributions

### Luca Crema

- #### Data gathering

  - Resarched datasets online and found one for free.
  - Determined the possible number of nodes and edges.

- #### `csv_to_graph.py`

  - Analyzed the dataset to determine useful columns and the types of errors.
  - Researched standard cleaning methods (like filtering, fixing, interpolation, copying) used in industry data science projects.
  - Applied the standard cleaning methods to the dataset.
  - Devised specific cleaning methods to avoid the filtering of too many rows.
  - Learned python library `argparse` to create a parametrized CLI script to clean and parse the dataset.
  - Learned python library `pandas` methods to have a more readable data cleaning pipeline.
  - Investigated different file formats to store the parsed graph.

- #### `notebook.ipynb`

  - Capitalization computation
  - Cycle detection
  - Node2Vec embedding

- #### `graph_library.py`

  - `max_k_nodes(G, k)`
  - `betweenness_centrality_percent(G, percentage=p)`
  - `connected_random_subgraph(G, n)`

### Riccardo Crociani

- #### notebook.ipynb

  - Load graph and basic information
  - Node-level feature
    - Betweenness centrality (approximated)
    - Closeness centrality
    - Clustering coefficient
  - Graphlet and motifs
    - ESU algorithm

- #### graph_library.py

  - closeness_centrality_matrix(G)
  - max_out_degree_vertex(G)
  - max_in_degree_vertex(G)
  - min_in_degree_vertex(G)
  - longest_path(G)
  - exclusive_neighborhood(G, v, Vp)
  - extend_subgraph(G, Vsubgraph, Vextension, v, k, k_subgraphs)
  - enumerate_subgraphs(G, k)
