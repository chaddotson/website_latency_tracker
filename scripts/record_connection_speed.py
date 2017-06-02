#!/usr/bin/env python3.6

from argparse import ArgumentParser
from csv import writer
from logging import basicConfig, getLogger, INFO, DEBUG
from os.path import exists
from speedtest import Speedtest
from time import time

logger = getLogger(__name__)


def parse_args():
    parser = ArgumentParser(description='Monitor upload, download, and latency.')
    parser.add_argument('tracking_file', help='File to save results to')
    parser.add_argument('-l', '--list', help='List available servers by distance.', default=False, action='store_true')
    parser.add_argument('-s', '--servers', default=None, nargs="*", help='Specific server id to test with.')
    parser.add_argument('-v', '--verbose', help='Verbose logs', default=False, action='store_true')

    return parser.parse_args()


def print_server_list():
    s = Speedtest()
    servers = s.get_servers([])

    for key in sorted(servers.keys()):
        for server in servers[key]:
            print("{d:.2f}km - {id} - {sponsor} ({name} {country})".format(**server))

    exit()


def do_speedtest(servers=None):
    if servers is None:
        servers = []
    s = Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download()
    s.upload()
    return s.results


def write_header(output):
    output.writerow(["timestamp", "lat", "lon", "distance", "sponsor_id", "sponsor", "ping", "download", "upload"])


def write_results(output, results):
    output.writerow([time(), results.server["lat"], results.server["lon"],
                     results.server["d"], results.server["id"], results.server["sponsor"],
                     results.ping, results.download, results.upload])


def main():

    logging_config = dict(level=INFO,
                          format='[%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s] %(message)s')
    basicConfig(**logging_config)

    args = parse_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    if args.list:
        print_server_list()

    add_header = False

    if not exists(args.tracking_file):
        logger.debug("File is new, add headers.")
        add_header = True

    with open(args.tracking_file, "a") as out:
        output = writer(out)

        if add_header:
            write_header(output)

        if args.servers:
            for server in args.servers:
                results = do_speedtest([server])
                write_results(output, results)

        else:
            results = do_speedtest()
            write_results(output, results)

    logger.info("Done")


if __name__ == "__main__":
    main()

