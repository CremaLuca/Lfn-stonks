"""
Loads a constituent CSV file and converts it to a newtorkx graph in weitghted edgelist format.
"""

__author__ = "Luca Crema"
__version__ = "0.1"

import argparse
import csv
from typing import List

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
    "FIGI"
]

# Define default CSV columns indexes
DEFAULT_ETF_TICKER_COLUMN: int = EXPECTED_COLUMNS.index("Composite Ticker")
DEFAULT_COMPONENT_TICKER_COLUMN: int = EXPECTED_COLUMNS.index("Constituent Ticker")
DEFAULT_MARKET_VALUE_COLUMN: int = EXPECTED_COLUMNS.index("Market Value")
DEFAULT_CURRENCY_COLUMN: int = EXPECTED_COLUMNS.index("Currency")


def main():
    parser = argparse.ArgumentParser(
        description='Loads a CSV file and converts it into a networkx graph in weitghted edgelist format.')
    parser.add_argument('filename', metavar='PATH', type=str, nargs=1,
                        help='path of the CSV file to parse.')
    parser.add_argument('-o', '--output', metavar='PATH', type=str, nargs='?', default='out_graph.edgeList',
                        help='path of the output file, default `out_graph.edgeList`.')
    csv_columns_group = parser.add_argument_group("CSV columns", "Location of the information in the CSV columns.")
    csv_columns_group.add_argument('--etf-ticker-column', metavar='INT', type=int,
                                   nargs='?', default=DEFAULT_ETF_TICKER_COLUMN,
                                   help=f"index of the column containing the ETF ticker, default `{DEFAULT_ETF_TICKER_COLUMN}`.")
    csv_columns_group.add_argument('--component-ticker-column', metavar='INT', type=int,
                                   nargs='?', default=DEFAULT_COMPONENT_TICKER_COLUMN,
                                   help=f"index of the column containing the component ticker, default `{DEFAULT_COMPONENT_TICKER_COLUMN}`.")
    csv_columns_group.add_argument('--market-value-column', metavar='INT', type=int,
                                   nargs='?', default=DEFAULT_MARKET_VALUE_COLUMN,
                                   help=f"index of the column containing the amount of $currency the ETF has of the component, default `{DEFAULT_MARKET_VALUE_COLUMN}`.")
    csv_columns_group.add_argument('--currency-column', metavar='INT', type=int, nargs='?', default=DEFAULT_CURRENCY_COLUMN,
                                   help=f"index of the column containing the currency of the market value, default `{DEFAULT_CURRENCY_COLUMN}`.")
    csv_parsing_group = parser.add_argument_group("CSV parsing", "Details about CSV parsing process.")
    csv_parsing_group.add_argument('--consider-first-line', default=False, action='store_true',
                                   help='use this when the first line of the CSV contains data instead of an header.')
    csv_parsing_group.add_argument('-d', '--delimiter', metavar='CHAR', type=str, nargs='?', default=',',
                                   help='delimiter character of columns for the input CSV file, default `,`.')
    csv_parsing_group.add_argument('-q', '--quotechar', metavar='CHAR', type=str, nargs='?', default='"',
                                   help='quote character of strings for the input CSV file, default `"`.')
    args = parser.parse_args()
    print(args)
    with open(args.filename[0], mode="r", newline='', encoding='utf-8', errors='?') as csvfile:
        if args.consider_first_line is False:
            csvfile.readline()  # Skip the first CSV header row
        with open(args.output, mode="w") as outfile:
            reader = csv.reader(csvfile, delimiter=args.delimiter, quotechar=args.quotechar)
            for row in reader:
                start_node = row[args.etf_ticker_column]
                end_node = row[args.component_ticker_column]
                weight = row[args.market_value_column]
                # Skip if no value
                if not start_node or not end_node or not weight:
                    continue
                # Skip if empty value
                if weight == " " or weight == "-" or end_node == " " or start_node == " ":
                    continue
                # Remove spaces from names
                if " " in start_node:
                    start_node = start_node.split(" ")[0]
                if " " in end_node:
                    end_node = end_node.split(" ")[0]
                # Remove self-loop edges
                if start_node == end_node:
                    continue
                # TODO: convert weight in non-USD to USD
                outfile.write(f"{start_node} {end_node} {weight}\n")
    print("Done!")


if __name__ == "__main__":
    main()
