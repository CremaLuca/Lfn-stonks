# Roadmap

Defines what there is to do and when more or less we should do it.

## Project presentation

By fri 29/10/21 we have to deliver the project presentation.

### Required information

- Title
- Motivation
  - Questions
  - Data
    - Where to find it
    - What kind of graph & attributes of nodes and edges
    - Number of nodes and edges
    - Expected shape
- Method
  - Computational problem
  - Algorithms
    - Which exact algos, and which approx, when do we switch between them
- Intended experiments
  - Implementations (where to find algos/libraries)
  - Experiments details
  - Machine for experiments

### Our information

#### Title

???

#### Motivation

We want to explore the process of data gathering, convert them to a graph and compute meaningful metrics on it.

#### Data

Exchanged Traded Funds (ETFs) components datasets.

##### Where to find it

Start from an initial dataset found for free [at this link](https://masterdatareports.com/), which is updated at the end of each month, and continue our search to find more freely available data.

##### What kind of graph

It is a weighted directed graph. The nodes can represent fund nodes or component nodes, note that a fund node can also be a component. Edges go from a fund node to a component node and the weight is the amount of money in euros the fund owns of that component.

##### Number of nodes and edges

The american and european financial market contains about 100.000 securities between stocks, bonds and funds, so we expect that order of magnitude for the nodes (the initial dataset contains 31.000 nodes). Each fund contains on average a few hundred components so we are expecting an order of magnitude of a milion edges (the initial dataset contains 420.000 edges).

##### Expected shape

