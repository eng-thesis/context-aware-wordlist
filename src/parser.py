import argparse
import logging
from pathlib import Path

from io_utils import load_content_from_file

_logging_levels = {1: logging.WARN, 2: logging.INFO, 3: logging.DEBUG}


def parse() -> tuple[str, str, int, Path, list[Path]]:
    parser = argparse.ArgumentParser(
        prog="context-aware-wordlist-generator",
        description="Generate context aware list of possible endpoints of provided webpage content",
    )

    parser.add_argument(
        "url",
        help="url of the webpage",
    )
    parser.add_argument(
        "html_content",
        help="HTML content of the webpage",
    )
    parser.add_argument(
        "-f",
        action="store_true",
        help="if set, treats `html_content` as a filename",
        dest="is_filename",
    )
    parser.add_argument(
        "-n",
        help="how many concurrent requests should be sent, default is 3",
        default=3,
        type=int,
    )
    parser.add_argument(
        "-v",
        type=int,
        choices=[0, 1, 2, 3],
        default=0,
        dest="verbosity",
        help="verbosity level: 0=ERROR (default), 1=WARN, 2=INFO, 3=DEBUG",
    )
    parser.add_argument(
        "-o",
        type=Path,
        help="path to file, where output should be saved",
        dest="output",
        required=False,
    )
    parser.add_argument(
        "-i",
        nargs="*",
        type=Path,
        help="input wordlists to merge with generated results, optional",
        dest="input_wordlists",
    )

    args = parser.parse_args()
    if args.verbosity:
        logging.getLogger().setLevel(_logging_levels[args.verbosity])

    if args.is_filename:
        return (
            args.url,
            load_content_from_file(Path(args.html_content)),
            args.n,
            args.output,
            args.input_wordlists,
        )
    return args.url, args.html_content, args.n, args.output, args.input_wordlists
