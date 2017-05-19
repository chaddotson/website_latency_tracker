#!/usr/bin/env python3.6

from argparse import ArgumentParser
from csv import writer
from logging import basicConfig, getLogger, INFO, DEBUG
import grequests
from os.path import exists
from time import time

logger = getLogger(__name__)


def parse_args():
    parser = ArgumentParser(description='Monitor websites for response times to load the headers.')
    parser.add_argument('tracking_file', help='File to save results to')
    parser.add_argument('urls', help='url list', nargs="+")
    parser.add_argument('-v', '--verbose', help='Verbose logs', default=False, action='store_true')

    return parser.parse_args()


if __name__ == "__main__":

    logging_config = dict(level=INFO,
                          format='[%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s] %(message)s')
    basicConfig(**logging_config)

    args = parse_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    add_header = False

    if not exists(args.tracking_file):
        logger.debug("File is new, add headers.")
        add_header = True

    with open(args.tracking_file, "a") as out:
        output = writer(out)

        if add_header:
            output.writerow(["timestamp", "url", "loadtime", "size"])

        logger.info("Starting tests")

        req = (grequests.get(url) for url in args.urls)

        resps = grequests.map(req)

        for resp in resps:
            if resp is not None:
                logger.info("Tested: %s - Response Time: %d - Size: %d",
                            resp.url, resp.elapsed.total_seconds(), len(resp.content))
                output.writerow([time(), resp.url, resp.elapsed.total_seconds(), len(resp.content)])

    logger.info("Done")

