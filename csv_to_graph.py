"""
Loads a constituent CSV file and converts it to a newtorkx graph in weitghted edgelist format.
"""

__author__ = "Luca Crema"
__version__ = "0.1"

import argparse
import logging
from typing import Dict, List

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)

# Expected CSV columns when parsing ConstituentData.csv file
EXPECTED_COLUMNS: List[str] = [
    "Sponsor",
    "Composite Ticker",
    "Composite Name",
    "Constituent Ticker",
    "Constituent Name",
    "Weighting",
    "Identifier",
    "Date",
    "Location",
    "Exchange",
    "Total Shares Held",
    "Notional Value",
    "Market Value",
    "Sponsor Sector",
    "Last Trade",
    "Currency",
    "BloombergSymbol",
    "BloombergExchange",
    "NAICSSector",
    "NAICSSubIndustry",
    "Coupon",
    "Maturity",
    "Rating",
    "Type",
    "SharesOutstanding",
    "MarketCap",
    "Earnings",
    "PE Ratio",
    "Face",
    "FIGI",
    "TimeZone",
    "DividendAmt",
    "XDate",
    "DividendYield",
    "RIC",
    "IssueType",
    "NAICSSector",
    "NAICSIndustry",
    "NAICSSubIndustry",
    "CUSIP",
    "ISIN",
    "FIGI",
]

# Define default CSV columns indexes
DEFAULT_ETF_TICKER_COLUMN: str = "Composite Ticker"
DEFAULT_COMPONENT_TICKER_COLUMN: str = "Constituent Ticker"
DEFAULT_MARKET_VALUE_COLUMN: str = "Market Value"
DEFAULT_CURRENCY_COLUMN: str = "Currency"
DEFAULT_ISIN_COLUMN: str = "ISIN"

# Currency conversion rates
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
TICKER_REGEX = r"([a-zA-Z0-9\.]{1,8})+"
WEIGHT_REGEX = r"[\+\-]?([0-9]*\.)?[0-9]+"
ISIN_REGEX = r"[a-zA-Z]{2}[0-9]{4,10}"


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Loads a CSV file and converts it into a networkx graph in weitghted edgelist format."
    )
    parser.add_argument("filename", metavar="PATH", type=str, nargs=1, help="path of the CSV file to parse.")
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        type=str,
        nargs=1,
        default=["out_graph"],
        help="path of the output file, default `out_graph.edgeList`.",
    )
    parser.add_argument(
        "--default-currency",
        metavar="CURRENCY",
        type=str,
        nargs=1,
        default=["USD"],
        help="default currency to use when it is not specified, default `USD`.",
    )
    parser.add_argument(
        "--no-currency-conversion",
        action="store_true",
        help="do not convert currencies to euros.",
    )
    parser.add_argument(
        "-log", "--loglevel", type=str, nargs=1, default=["warning"], help="provide logging level, default `warning`."
    )
    # CSV columns group
    csv_columns_group = parser.add_argument_group("CSV columns", "Location of the information in the CSV columns.")
    csv_columns_group.add_argument(
        "--etf-ticker-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_ETF_TICKER_COLUMN,
        help=f"name of the column containing the ETF ticker, default `{DEFAULT_ETF_TICKER_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--component-ticker-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_COMPONENT_TICKER_COLUMN,
        help=f"name of the column containing the component ticker, default `{DEFAULT_COMPONENT_TICKER_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--market-value-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_MARKET_VALUE_COLUMN,
        help=f"name of the column containing the amount of $currency the ETF has of the component, \
            default `{DEFAULT_MARKET_VALUE_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--currency-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_CURRENCY_COLUMN,
        help=f"name of the column containing the currency of the market value, default `{DEFAULT_CURRENCY_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--isin-column",
        metavar="STR",
        type=str,
        nargs="?",
        default=DEFAULT_ISIN_COLUMN,
        help=f"name of the column containing the isin of the component, default `{DEFAULT_ISIN_COLUMN}`.",
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
        help="delimiter character of columns for the input CSV file, default `,`.",
    )
    csv_parsing_group.add_argument(
        "-q",
        "--quotechar",
        metavar="CHAR",
        type=str,
        nargs="?",
        default='"',
        help='quote character of strings for the input CSV file, default `"`.',
    )
    return parser


def to_euros(value: float, currency: str) -> float:
    """
    Convert a value in a given currency to euros.
    """
    if currency not in CURRENCY_CONVERSION_RATES:
        raise ValueError(f"Unknown currency `{currency}`.")
    return value * CURRENCY_CONVERSION_RATES[currency]


def main():
    parser = make_parser()
    args = parser.parse_args()  # Parse command line arguments
    logging.basicConfig(level=args.loglevel[0].upper())

    # Load CSV file
    df = pd.read_csv(args.filename[0], sep=args.delimiter, quotechar=args.quotechar, encoding="utf-8", na_values=" ")
    # Filter out the unwanted columns
    WANTED_COLUMNS = [
        args.etf_ticker_column,
        args.component_ticker_column,
        args.market_value_column,
        args.currency_column,
        args.isin_column,
    ]
    df = df[WANTED_COLUMNS]
    print("After columns filter\n", df.describe())
    # Fill missing currency values
    if not args.no_currency_conversion:
        df.fillna(value={args.currency_column: args.default_currency[0]}, inplace=True)
    print("After currency fillNaN\n", df.describe())
    # Remove ticker location (like .JP .AU .HK )
    df[args.etf_ticker_column] = df[args.etf_ticker_column].str.replace(r"(\.|-| )+.*", "", regex=True)
    df[args.component_ticker_column] = df[args.component_ticker_column].str.replace(r"(\.|-| )+.*", "", regex=True)
    print("After ticker location removal\n", df.describe())
    # Remove "CASH" from tickers
    df[args.component_ticker_column] = df[args.component_ticker_column].str.replace("CASH_", "", regex=False)
    # TODO: set the currency to the remaining part of the ticker
    print("After 'CASH_' removal\n", df.describe())
    # Rename cash tickers to their currency
    df[args.component_ticker_column] = df[args.component_ticker_column].str.replace(
        "0", args.default_currency[0], regex=False
    )
    print("After '0' (cash) removal\n", df.describe())
    # Fill missing ticker values
    df.loc[df[args.component_ticker_column].isnull(), args.component_ticker_column] = df.loc[
        df[args.component_ticker_column].isnull(), args.isin_column
    ].map(
        df.loc[df[args.isin_column].notnull()]
        .groupby(args.isin_column)
        .aggregate({args.component_ticker_column: "first"})[args.component_ticker_column]
    )
    print("After ticker fill\n", df.describe())
    # Fill the missing isin values
    df.loc[df[args.isin_column].isnull(), args.isin_column] = df.loc[
        df[args.isin_column].isnull(), args.component_ticker_column
    ].map(
        df.loc[df[args.component_ticker_column].notnull()]
        .groupby(args.component_ticker_column)
        .aggregate({args.isin_column: "first"})[args.isin_column]
    )
    print("After isin fill\n", df.describe())
    # Filter out the invalid tickers
    df = df[
        (df[args.etf_ticker_column].notnull() & df[args.etf_ticker_column].str.match(TICKER_REGEX))
        & (df[args.component_ticker_column].notnull() & df[args.component_ticker_column].str.match(TICKER_REGEX))
    ]
    print("After invalid tickers removal\n", df.describe())
    # Remove indices (whose ticker start with .)
    df = df[df[args.etf_ticker_column].str.startswith(".") == False]  # noqa: E712
    print("After indices removal\n", df.describe())
    # Get the rows with same ticker but different isin
    # df_same_ticker_diff_isin = df[df[args.component_ticker_column].duplicated(
    #    keep=False) & df[args.isin_column].duplicated(keep=False)].sort_values(args.component_ticker_column)
    # print("Same ticker, different isin\n", df_same_ticker_diff_isin.head(20))
    # Rename market value column to weight
    df.rename(columns={args.market_value_column: "weight"}, inplace=True)
    # Create the networkx graph edges
    G = nx.from_pandas_edgelist(
        df,
        source=args.etf_ticker_column,
        target=args.component_ticker_column,
        edge_attr="weight",
        create_using=nx.DiGraph(),
    )
    # Add attributes to the nodes
    # node_data = df[[args.component_ticker_column, args.isin_column]].drop_duplicates()
    # print("Duplicated tickers\n", node_data[node_data.duplicated(
    #    [args.component_ticker_column]) == True].sort_values(args.component_ticker_column).head(20))
    # print("Node data\n", node_data.set_index(args.component_ticker_column).to_dict('index'))
    #  isin attribute
    # nx.set_node_attributes(G, node_data.set_index(args.component_ticker_column).to_dict('index'))
    # Store the graph as GML file
    nx.write_gml(G, f"{args.output[0]}.gml")
    print("Done!")


if __name__ == "__main__":
    main()
