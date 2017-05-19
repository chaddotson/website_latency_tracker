from argparse import ArgumentParser
from csv import DictReader
from datetime import datetime
from matplotlib import dates
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as mpl
import numpy as np


def parse_args():
    parser = ArgumentParser(description='Graph website response data.')
    parser.add_argument('tracking_file', help='File to read results from')
    parser.add_argument('url', help='url', nargs="?")
    parser.add_argument('-o', '--out', help='Output file', default=False, action='store_true')
    parser.add_argument('-l', '--list', help='List urls', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose logs', default=False, action='store_true')

    return parser.parse_args()


def read_monitor_file(filename):
    contents = []
    with open(filename, "r") as infile:
        incsv = DictReader(infile)

        for rec in incsv:
            contents.append(rec)

    return contents


if __name__ == "__main__":
    args = parse_args()
    contents = read_monitor_file(args.tracking_file)

    if args.list:
        print("Found urls:")
        for url in ({rec["url"] for rec in contents}):
            print(url)
        exit()

    contents = [rec for rec in contents if rec["url"] == args.url]

    if not len(contents):
        print("No records exist for " + args.url)
        exit()

    x = np.array([rec["timestamp"] for rec in contents])
    y = np.array([float(rec["loadtime"]) for rec in contents])

    x = [datetime.fromtimestamp(float(rec["timestamp"])) for rec in contents]
    x = dates.date2num(x)  # converted

    fig = mpl.figure(figsize=(7, 6))

    axes = fig.add_subplot(1, 1, 1)
    axes.set_xticklabels(axes.xaxis.get_majorticklabels(), rotation=90)
    axes.xaxis.set_major_formatter(DateFormatter('%m/%d/%Y - %H:%M:%S'))
    axes.xaxis_date()
    mpl.tight_layout()

    plt = axes.plot(x, y)

    mpl.show()
