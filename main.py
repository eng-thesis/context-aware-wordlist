from model import WordlistGenerator
from model.config import GeneratorConfig
from parser import parse

if __name__ == "__main__":
    url, html_content = parse()
    print("DEBUG", f"{url = }, {html_content = }")
    config = GeneratorConfig()  # type: ignore
    print("DEBUG", config)
    generator = WordlistGenerator(config)
    print("DEBUG", generator)
    response = generator.generate(url, html_content)
    print("DEBUG", response)
    print("DEBUG", ", ".join(response.endpoints))
