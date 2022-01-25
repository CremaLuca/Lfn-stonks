**Partecipants**:

- Luca Crema 2026827
- Riccardo Crociani 2022466

## Title

How hard is it to work on a new raw dataset? Which **useful** metrics can be computed in reasonable time?

## Motivation

We want to explore the process of data gathering, convert them to a graph and compute meaningful metrics on it.

## What changed

- We are no more looking for new data as the data we already have are enough time expensive to analyze.
- We will mainly focus on node-level metrics and spend less efforts on network patterns as we realised that they don't yield interesting information for our specific problem.

## What we have done

- We managed to parse the data from the initial ETF dataset into a directed networkx graph.
- We tried to clean the dataset as much as possible, filling the gaps and normalized naming by adopting the same naming notation for each record.
- We adapted existing library functions to compute or approximate node-level metrics (closeness centrality, betweenness centrality and clustering coefficient).
- We devised a function to compute a random *connected* subgraph.
