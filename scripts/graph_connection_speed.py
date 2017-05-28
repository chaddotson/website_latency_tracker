from argparse import ArgumentParser
from configparser import RawConfigParser
from csv import DictReader
from datetime import datetime, timedelta
from io import BytesIO
from logging import basicConfig, getLogger, INFO, DEBUG
from matplotlib import dates
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as mpl
import numpy as np
from tempfile import NamedTemporaryFile
from tweepy import API, OAuthHandler


logger = getLogger(__name__)


def parse_args():
    parser = ArgumentParser(description='Graph website response data.')
    parser.add_argument('tracking_file', help='File to read results from')
    parser.add_argument('-f', '--filter', help='Filtering ids', nargs="+", default=None)
    parser.add_argument('-d', '--days', help='how many days to graph', type=float, default=3.0)
    parser.add_argument('-o', '--out', help='Output file', type=str)
    parser.add_argument('-t', '--tweet', help='Output as tweet (arg = twitter.cfg)', type=str)
    parser.add_argument('-s', '--show', help='Show', default=False, action='store_true')
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



class NoRecordsError(RuntimeError):
    pass


class GraphOutput(object):
    def create_output(self):
        return None


class DisplayGraphOutput(GraphOutput):
    def create_output(self):
        mpl.show()

        return None


class FileGraphOutput(GraphOutput):
    def __init__(self, filename, image_format="png", reset_seek=True):
        self._filename = filename
        self._image_format = image_format
        self._reset_seek = reset_seek

    def create_output(self):
        mpl.savefig(self._filename, format=self._image_format)
        return self._filename


class BytesGraphOutput(GraphOutput):
    def __init__(self, image_format="png", reset_seek=True):
        self._image_format = image_format
        self._reset_seek = reset_seek

    def create_output(self):
        results = BytesIO()
        mpl.savefig(results, format=self._image_format)

        if self._reset_seek:
            results.seek(0)

        return results


class TweetGraphOutput(BytesGraphOutput):
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)

        self._api = API(auth)

        super(TweetGraphOutput, self).__init__(image_format="png")

    def create_output(self):
        output = super(TweetGraphOutput, self).create_output()

        with NamedTemporaryFile(suffix=".png") as f:
            f.write(output.read())

            print(f.name)

            self._api.update_with_media(f.name, "Test!")

        return output


def generate_graph(tracking_file, days, output_strategy, filter_list=None):

    logger.info("Source File: %s", tracking_file)
    logger.info("Days: %f", days)
    logger.info("Output: %s", output_strategy)
    logger.info("Filter: %s", filter_list)

    records = read_monitor_file(tracking_file)
    start_timestamp = (datetime.now() - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    filtered = [rec for rec in records if float(rec["timestamp"]) >= start_timestamp and (filter_list is None or rec["sponsor_id"] in filter_list)]

    logger.debug("Start: %f / %s", start_timestamp, datetime.fromtimestamp(start_timestamp))
    logger.debug("First: %f / %s", float(filtered[0]["timestamp"]), datetime.fromtimestamp(float(filtered[0]["timestamp"])))

    if not len(filtered):
        raise NoRecordsError()

    x = [dates.date2num(datetime.fromtimestamp(float(rec["timestamp"]))) for rec in filtered]
    y = np.array([float(rec["download"]) / 1000000.0 for rec in filtered])

    fig = mpl.figure(figsize=(7, 6))

    axes = fig.add_subplot(1, 1, 1)
    axes.set_xticklabels(axes.xaxis.get_majorticklabels(), rotation=90)
    axes.xaxis.set_major_formatter(DateFormatter('%m/%d/%Y - %H:%M:%S'))
    axes.xaxis_date()
    mpl.tight_layout()

    plt = axes.plot(x, y)

    return output_strategy.create_output()


def list_sites(tracking_file):
    records = read_monitor_file(tracking_file)
    print("Found urls:")
    for url in ({rec["url"] for rec in records}):
        print(url)


if __name__ == "__main__":
    logging_config = dict(level=INFO,
                          format='[%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s] %(message)s')
    basicConfig(**logging_config)

    args = parse_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    if args.list:
        list_sites(args.tracking_file)
        exit()

    output_using = None

    if args.show:
        output_using = DisplayGraphOutput()
    elif args.out:
        output_using = FileGraphOutput(args.out)
    # elif args.bytes:
    #     output_using = BytesGraphOutput(format="png")
    #     results = generate_graph(args.tracking_file, output_strategy=output_using)
    #
    #     with open("test.png", "wb") as f:
    #         f.write(results.read())
    #     exit()

    elif args.tweet:
        config = RawConfigParser()
        config.read(args.tweet)
        output_using = TweetGraphOutput(config.get("TWITTER", "CONSUMER_KEY"),
                                        config.get("TWITTER", "CONSUMER_SECRET"),
                                        config.get("TWITTER", "ACCESS_KEY"),
                                        config.get("TWITTER", "ACCESS_SECRET"))
    else:
        logger.error("No valid output type specified.  Unable to continue.")
        exit()

    results = generate_graph(args.tracking_file, days=args.days, output_strategy=output_using, filter_list=args.filter)

    logger.info("Done")