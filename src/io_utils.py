from pathlib import Path
from typing import Iterable


def write_output(endpoints: Iterable[str], path: Path | None = None) -> None:
    if path is None:
        print(*endpoints, sep="\n")
        return

    path.parent.mkdir(exist_ok=True, parents=True)
    with open(path, "w") as file:
        print(*endpoints, sep="\n", file=file)


def load_content_from_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {str(path)!r}")
    return path.read_text()


def load_wordlists(paths: list[Path]) -> set[str]:
    endpoints: set[str] = set()
    for path in paths:
        endpoints.update(load_content_from_file(path).splitlines())

    return endpoints
