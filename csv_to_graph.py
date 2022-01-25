#!
"""
Loads a constituent CSV file and converts it to a newtorkx graph in weitghted edgelist format.
Can be used both as a command-line script and as a python imporable module.
"""

import pandas as pd
import networkx as nx
from typing import Dict, List
import logging
import argparse

__author__ = "Luca Crema"
__version__ = "1.0"
__all__ = ["parse_csv"]


logger: logging.Logger = logging.getLogger(__name__)


# Define default CSV columns indexes
DEFAULT_ETF_TICKER_COLUMN: str = "Composite Ticker"
DEFAULT_COMPONENT_TICKER_COLUMN: str = "Constituent Ticker"
DEFAULT_MARKET_VALUE_COLUMN: str = "Market Value"
DEFAULT_CURRENCY_COLUMN: str = "Currency"
DEFAULT_ISIN_COLUMN: str = "ISIN"

# Currency conversion rates, should be updated periodically
DEFAULT_CURRENCY: str = "EUR"
CURRENCY_CONVERSION_RATES: Dict[str, float] = {
    "EUR": 1.0,
    "USD": 0.858,
    "GBP": 1.181,
    "JPY": 0.007563,
    "SGD": 0.637,
    "CHF": 0.9375,
    "MYR": 0.2068,
    "IDR": 0.00006069,
}

# List of values that are considered as invalid
TICKER_REGEX: str = r"([a-zA-Z0-9\.]{1,8})+"
WEIGHT_REGEX: str = r"[\+\-]?([0-9]*\.)?[0-9]+"
ISIN_REGEX: str = r"[a-zA-Z]{2}[0-9]{4,10}"
LOCATION_REGEX: str = r"(\.|-| )+.*"


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Loads a CSV file and converts it into a networkx graph in weitghted edgelist format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("filename", metavar="PATH", type=str, nargs="?", help="path of the CSV file to parse.")
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        type=str,
        nargs="?",
        default=["out_graph"],
        help="path of the output file.",
    )
    parser.add_argument(
        "--default-currency",
        metavar="CURRENCY",
        type=str,
        nargs="?",
        default=["USD"],
        help="default currency to use when it is not specified.",
    )
    parser.add_argument(
        "--no-currency-conversion",
        action="store_true",
        help="do not convert currencies to euros.",
    )
    parser.add_argument("-log", "--loglevel", type=str, nargs="?", default="warning", help="provide logging level.")
    # CSV columns group
    csv_columns_group = parser.add_argument_group("CSV columns", "Location of the information in the CSV columns.")
    csv_columns_group.add_argument(
        "--etf-ticker-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_ETF_TICKER_COLUMN,
        help="name of the column containing the ETF ticker.",
    )
    csv_columns_group.add_argument(
        "--component-ticker-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_COMPONENT_TICKER_COLUMN,
        help="name of the column containing the component ticker.",
    )
    csv_columns_group.add_argument(
        "--market-value-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_MARKET_VALUE_COLUMN,
        help="name of the column containing the amount of $currency the ETF has of the component.",
    )
    csv_columns_group.add_argument(
        "--currency-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_CURRENCY_COLUMN,
        help="name of the column containing the currency of the market value.",
    )
    csv_columns_group.add_argument(
        "--isin-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_ISIN_COLUMN,
        help="name of the column containing the isin of the component.",
    )
    # CSV parsing group
    csv_parsing_group = parser.add_argument_group("CSV parsing", "Details about CSV parsing process.")
    csv_parsing_group.add_argument(
        "-d",
        "--delimiter",
        metavar="CHAR",
        type=str,
        nargs="?",
        default=",",
        help="delimiter character of columns for the input CSV file.",
    )
    csv_parsing_group.add_argument(
        "-q",
        "--quotechar",
        metavar="CHAR",
        type=str,
        nargs="?",
        default='"',
        help="quote character of strings for the input CSV file.",
    )
    return parser


def _to_uniform_currency(value: float, currency: str, ignore_unknown: bool = False) -> float:
    """
    Convert a value in a given currency to euros.
    """
    if currency not in CURRENCY_CONVERSION_RATES:
        # Return a default 0.0 value if the currency is unknown and we don't care about it
        if ignore_unknown:
            return 0.0
        raise ValueError(f"Unknown currency `{currency}`.")
    return value * CURRENCY_CONVERSION_RATES[currency]


def _replace(df: pd.DataFrame, column: str, pattern: str, replacement: str) -> pd.DataFrame:
    """
    Replace a pattern in a dataframe.
    """
    df[column] = df[column].str.replace(pattern, replacement, regex=True)
    return df


def _fill_column(df: pd.DataFrame, missing_column: str, filler_column: str) -> pd.DataFrame:
    """
    Replaces empty "missing_column" values with the same-column value from another row that has
    the same "filler_column" value.
    """
    df.loc[df[missing_column].isnull(), missing_column] = df.loc[df[missing_column].isnull(), filler_column].map(
        df.loc[df[filler_column].notnull()].groupby(filler_column).aggregate({missing_column: "first"})[missing_column]
    )
    return df


def _filter_regex(df: pd.DataFrame, column: str, regex: str) -> pd.DataFrame:
    """
    Filters a dataframe by a regex.
    """
    return df[df[column].notnull() & df[column].str.match(regex)]


def _describe(df: pd.DataFrame, description: str = None) -> pd.DataFrame:
    """
    Outputs the describe method of a dataframe on the logger at DEBUG level.
    """
    if description:
        logger.debug(description)
    logger.debug(f"\n{df.describe(include='all')}")
    return df


def _to_float(value: str) -> float:
    """
    Convert a string to a float.

    Returns:
        The float value of the string if it is a valid float, else 0.0.
    """
    try:
        return float(value)
    except ValueError:
        return 0.0


def _convert_currency(df: pd.DataFrame, market_value_column: str, currency_column: str) -> pd.DataFrame:
    """
    Converts the currency to the default one and changes the currency column value.
    """
    df[[market_value_column, currency_column]] = df[[market_value_column, currency_column]].apply(
        lambda row: (
            _to_uniform_currency(_to_float(row[market_value_column]), row[currency_column]),
            DEFAULT_CURRENCY,
        ),
        axis=1,
        result_type="broadcast",
    )
    return df


def parse_csv(
    filename: str,
    etf_ticker_column: str = DEFAULT_ETF_TICKER_COLUMN,
    component_ticker_column: str = DEFAULT_COMPONENT_TICKER_COLUMN,
    market_value_column: str = DEFAULT_MARKET_VALUE_COLUMN,
    currency_column: str = DEFAULT_CURRENCY_COLUMN,
    isin_column: str = DEFAULT_ISIN_COLUMN,
    delimiter: str = ",",
    quotechar: str = '"',
    default_currency: str = "USD",
    **kwargs,
) -> nx.DiGraph:
    """
    Parses a dataset in CSV format and returns a Netoworkx DiGraph.

    Parameters:
        filename: path of the CSV file to parse.

    Returns:
        A Networkx DiGraph with edges containing market value as 'weight' attribute.
    """
    # Load CSV file
    df: pd.DataFrame = pd.read_csv(filename, sep=delimiter, quotechar=quotechar, encoding="utf-8", na_values=" ")
    # Filter out the unwanted columns
    wanted_columns: List[str] = [
        etf_ticker_column,
        component_ticker_column,
        market_value_column,
        currency_column,
        isin_column,
    ]
    df = df[wanted_columns]

    df = (
        # Remove rows without market value
        df.pipe(lambda df: df.dropna(subset=[market_value_column]))
        .pipe(_describe, "Filtered rows without market value")
        # Remove exact duplicate rows
        .pipe(lambda df: df.drop_duplicates())
        .pipe(_describe, "Filtered exactly duplicate rows")
        # Fill missing currency values
        .pipe(lambda df: df.fillna(value={currency_column: default_currency[0]}, inplace=False))
        .pipe(_describe, "Filled NaN currency values")
        # Remove ticker columns location (like .JP .AU .HK )
        .pipe(_replace, etf_ticker_column, LOCATION_REGEX, "")
        .pipe(_replace, component_ticker_column, LOCATION_REGEX, "")
        .pipe(_describe, "Removed ticker locations")
        # Remove "CASH" from tickers
        # TODO: set the currency to the remaining part of the ticker
        .pipe(_replace, component_ticker_column, "CASH_", "")
        # Rename cash tickers ("0") to their currency
        .pipe(_replace, component_ticker_column, "0", default_currency[0])
        .pipe(_describe, "Renamed cash constituents")
        # Fill missing tickers with the ticker from other components with the same ISIN
        .pipe(_fill_column, missing_column=component_ticker_column, filler_column=isin_column)
        # Fill missing isin with the isin from other components with the same ticker
        .pipe(_fill_column, missing_column=isin_column, filler_column=component_ticker_column)
        .pipe(_describe, "Filled ticker and ISIN columns")
        # Filter out the invalid tickers with the regex
        .pipe(_filter_regex, column=etf_ticker_column, regex=TICKER_REGEX)
        .pipe(_filter_regex, column=component_ticker_column, regex=TICKER_REGEX)
        .pipe(_describe, "Filtered invalid tickers")
        # Remove indices (etf tickers that start with a dot)
        .pipe(lambda df: df[df[etf_ticker_column].str.startswith(".") == False])  # noqa: E712
        .pipe(_describe, "Removed indices")
    )
    # Avoid currency conversion if not wanted
    if "no-currency-conversion" not in kwargs or not kwargs["no-currency-conversion"]:
        df = (
            # Uniform currencies
            df.pipe(
                _convert_currency,
                market_value_column,
                currency_column,
            ).pipe(_describe, f"Converted all currencies to {DEFAULT_CURRENCY}")
        )
    # Rename market value column to weight
    df.rename(columns={market_value_column: "weight"}, inplace=True)
    # Create the networkx graph edges
    return nx.from_pandas_edgelist(
        df,
        source=etf_ticker_column,
        target=component_ticker_column,
        edge_attr="weight",
        create_using=nx.DiGraph(),
    )


def main():
    """
    Parses the command line arguments, calls the `parse_csv` function and outputs the graph to a gml file.
    """
    parser = _make_parser()
    args = parser.parse_args()  # Parse command line arguments
    logging.basicConfig(level=args.loglevel.upper())

    nx.write_gml(parse_csv(**vars(args)), f"{args.output[0]}.gml")
    logger.info("Done!")


"""
The module can be used both as a command-line script and as an imported python module.
"""
if __name__ == "__main__":
    main()
