#!/usr/bin/env python3.6


from argparse import ArgumentParser
from csv import writer
from logging import basicConfig, getLogger, INFO, DEBUG
import grequests
from time import sleep, time

logger = getLogger(__name__)


def parse_args():
    parser = ArgumentParser(description='Monitor websites for response times to load the headers.')
    parser.add_argument('tracking_file', help='File to save results to')
    parser.add_argument('urls', help='url list', nargs="+")
    parser.add_argument('-n', '--new', help='Start new file / erase if present.', default=False, action='store_true')
    parser.add_argument('-d', '--delay', help='seconds between tests', type=int, default=300)
    parser.add_argument('-v', '--verbose', help='Verbose logs', default=False, action='store_true')

    return parser.parse_args()


if __name__ == "__main__":

    logging_config = dict(level=INFO,
                          format='[%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s] %(message)s')
    basicConfig(**logging_config)

    args = parse_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    mode = "w" if args.new else "a"

    try:
        while True:
            logger.debug("Testing")

            req = (grequests.get(url) for url in args.urls)
            start = time()
            resps = grequests.map(req)

            with open(args.tracking_file, mode) as out:
                output = writer(out)

                for resp in resps:
                    logger.info("Tested: %s - Response Time: %d - Size: %d",
                                 resp.url, resp.elapsed.total_seconds(), len(resp.content))
                    output.writerow([time(), resp.url, resp.elapsed.total_seconds(), len(resp.content)])

            sleep(args.delay)
            mode = "a"

    except KeyboardInterrupt:
        logger.info("Exiting...")

