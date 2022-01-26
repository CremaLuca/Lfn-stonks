# Learning from networks project - Stonks

The "Stonks" project main target is to find out how hard it is to find, obtain and clean a raw tabular ([relational database](https://en.wikipedia.org/wiki/Relational_database), [csv](https://en.wikipedia.org/wiki/Comma-separated_values), ...) dataset for a topic of interest, leaving the detailed data analysis to field experts.
In our case the topic chosen is "Stock [ETFs](https://www.investopedia.com/terms/e/etf.asp) and their [underlying assets](https://www.investopedia.com/terms/u/underlying-asset.asp)", but most of the concepts are reusable in other fields.

## Getting started

Start off by downloading the dataset from [here](https://masterdatareports.com/).

```sh
curl https://masterdatareports.com/Download-Files/ConstituentData42.csv -o dataset.csv
```

Optional: create a virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Parse the csv dataset to a graph in `gml` format using the `csv_to_graph` module.

```sh
pip install -r requirements.txt
python csv_to_dataset.py dataset.csv -o out_graph
```

Now you are ready to run the experiments in the Jupyter notebook `notebook.ipynb`.

## Contributing

### Pre-commit checks

Before opening a pull request you have to install `pre-commit`s and run it to check black, flake8 and mypy.

```bash
pip install pre-commit
pre-commit run

pre-commit install
git add -A
git commit -m "feat: new stuff"
```

### Conventional commits

Try to stick as much as possible to conventional commits guidelines for your commit messages.
