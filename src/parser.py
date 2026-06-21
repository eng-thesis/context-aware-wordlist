import argparse
from pathlib import Path


def _load_content_from_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {str(path)!r}")
    return path.read_text()


def parse() -> tuple[str, str]:
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

    args = parser.parse_args()
    if args.is_filename:
        return args.url, _load_content_from_file(Path(args.html_content))
    return args.url, args.html_content
