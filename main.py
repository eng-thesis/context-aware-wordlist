from common.logging import get_logger
from io_utils import load_wordlists, write_output
from model import WordlistGenerator
from model.config import GeneratorConfig
from parser import parse

log = get_logger(__name__)


def main() -> None:
    url, html_content, n, output, input_wordlists = parse()
    log.debug(f"{url = }, {html_content[:500] = }")

    config = GeneratorConfig()  # type: ignore
    log.info(f"Using config: {config}")

    generator = WordlistGenerator(config)
    response = generator.generate_multiple(url, html_content, n=n)
    log.debug(response)
    log.debug(f"{len(response) = }")

    endpoints = set().union(*[set(r.endpoints) for r in response])

    if input_wordlists:
        log.debug(f"{endpoints = }")
        endpoints_loaded = load_wordlists(input_wordlists)
        log.debug(f"{endpoints_loaded = }")
        endpoints.update(endpoints_loaded)

    write_output(endpoints, output)


if __name__ == "__main__":
    main()
