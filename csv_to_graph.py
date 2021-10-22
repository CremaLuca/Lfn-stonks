"""
Loads a constituent CSV file and converts it to a newtorkx graph in weitghted edgelist format.
"""

__author__ = "Luca Crema"
__version__ = "0.1"

import argparse
import csv
import logging
import re
from typing import Dict, List

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
DEFAULT_ETF_TICKER_COLUMN: int = EXPECTED_COLUMNS.index("Composite Ticker")
DEFAULT_COMPONENT_TICKER_COLUMN: int = EXPECTED_COLUMNS.index("Constituent Ticker")
DEFAULT_MARKET_VALUE_COLUMN: int = EXPECTED_COLUMNS.index("Market Value")
DEFAULT_CURRENCY_COLUMN: int = EXPECTED_COLUMNS.index("Currency")

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
        default="out_graph.edgeList",
        help="path of the output file, default `out_graph.edgeList`.",
    )
    parser.add_argument(
        "--default-currency",
        metavar="CURRENCY",
        type=str,
        nargs=1,
        default="USD",
        help="default currency to use when it is not specified, default `USD`.",
    )
    parser.add_argument(
        "--no-currency-conversion",
        action="store_true",
        help="do not convert currencies to euros.",
    )
    parser.add_argument(
        "-log", "--loglevel", type=str, nargs=1, default="warning", help="provide logging level, default `warning`."
    )
    csv_columns_group = parser.add_argument_group("CSV columns", "Location of the information in the CSV columns.")
    csv_columns_group.add_argument(
        "--etf-ticker-column",
        metavar="INT",
        type=int,
        nargs="?",
        default=DEFAULT_ETF_TICKER_COLUMN,
        help=f"index of the column containing the ETF ticker, default `{DEFAULT_ETF_TICKER_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--component-ticker-column",
        metavar="INT",
        type=int,
        nargs="?",
        default=DEFAULT_COMPONENT_TICKER_COLUMN,
        help=f"index of the column containing the component ticker, default `{DEFAULT_COMPONENT_TICKER_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--market-value-column",
        metavar="INT",
        type=int,
        nargs="?",
        default=DEFAULT_MARKET_VALUE_COLUMN,
        help=f"index of the column containing the amount of $currency the ETF has of the component, \
            default `{DEFAULT_MARKET_VALUE_COLUMN}`.",
    )
    csv_columns_group.add_argument(
        "--currency-column",
        metavar="INT",
        type=int,
        nargs="?",
        default=DEFAULT_CURRENCY_COLUMN,
        help=f"index of the column containing the currency of the market value, default `{DEFAULT_CURRENCY_COLUMN}`.",
    )
    csv_parsing_group = parser.add_argument_group("CSV parsing", "Details about CSV parsing process.")
    csv_parsing_group.add_argument(
        "--consider-first-line",
        default=False,
        action="store_true",
        help="use this when the first line of the CSV contains data instead of an header.",
    )
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
    with open(args.filename[0], mode="r", newline="", encoding="utf-8", errors="?") as csvfile:
        if args.consider_first_line is False:
            csvfile.readline()  # Skip the first CSV header row
        with open(args.output, mode="w") as outfile:
            reader = csv.reader(csvfile, delimiter=args.delimiter, quotechar=args.quotechar)
            for row in reader:
                # TODO: pass twice: save the isin the first time and the second time map non-existing
                # end_nodes to the isin
                start_node: str = row[args.etf_ticker_column]
                end_node: str = row[args.component_ticker_column]
                weight: str = row[args.market_value_column]
                currency: str = row[args.currency_column]
                # Skip if None or empty
                if not any([start_node, end_node, weight]):
                    continue
                # Discard indices
                if start_node[0] == ".":
                    continue
                # Remove spaces from names
                if " " in start_node:
                    start_node = start_node.split(" ")[0]
                if " " in end_node:
                    end_node = end_node.split(" ")[0]
                # Skip if value is invalid
                if not all(re.match(TICKER_REGEX, value) for value in [start_node, end_node]) or not re.match(
                    WEIGHT_REGEX, weight
                ):
                    logger.debug(
                        f"discarded {[start_node, end_node, weight, currency]}: TICKER_REGEX or \
                          WEIGHT_REGEX did not match"
                    )
                    continue
                # Remove self-loop edges
                if start_node == end_node:
                    # NOTE: this means the node is an ETF
                    continue
                # Parse the weight to float
                try:
                    weight = float(weight)
                except ValueError:
                    logger.debug(f"discarded {[start_node, end_node, weight, currency]}: `{weight}` is not a float")
                    continue
                # Convert weight in non-EUR to EUR
                if not args.no_currency_conversion:
                    # Check currency
                    if not re.match("([a-zA-Z]+){1,4}", currency):
                        logger.debug(f"converted currency `{currency}` to {args.default_currency}")
                        currency = args.default_currency
                    weight = to_euros(weight, currency)
                outfile.write(f"{start_node} {end_node} {weight}\n")
    print("Done!")


if __name__ == "__main__":
    main()
