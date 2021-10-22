"""
Loads a constituent CSV file and converts it to a newtorkx graph in weitghted edgelist format.
"""

__author__ = "Luca Crema"
__version__ = "0.1"

import argparse
import csv

COLUMNS = [
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


def main():
    parser = argparse.ArgumentParser(
        description='Loads a CSV file and converts it into a networkx graph in weitghted edgelist format.')
    parser.add_argument('filename', metavar='PATH', type=str, nargs=1,
                        help='path of the CSV file to parse.')
    parser.add_argument('-o', '--output', metavar='PATH', type=str, nargs='?', default='out_graph.edgeList',
                        help='path of the output file, default `out_graph.edgeList`.')
    parser.add_argument('-d', '--delimiter', metavar='CHAR', type=str, nargs='?', default=',',
                        help='delimiter character of columns for the input CSV file, default `,`.')
    parser.add_argument('-q', '--quotechar', metavar='CHAR', type=str, nargs='?', default='"',
                        help='quote character of strings for the input CSV file, default `"`.')
    args = parser.parse_args()
    with open(args.filename[0], mode="r", newline='', encoding='utf-8', errors='?') as csvfile:
        # Skip the first CSV row
        next(csvfile)
        with open(args.output, mode="w") as outfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                start_node = row[1]
                end_node = row[3]
                weight = row[12]
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
