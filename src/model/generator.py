from google import genai
from google.genai import types

from model.config import GeneratorConfig
from model.exceptions import EmptyResponseTextError
from model.models import WordlistResponse
from model.prompt import GENERATOR_PROMPT


class WordlistGenerator:
    def __init__(self, config: GeneratorConfig) -> None:
        self._config = config
        self._client = genai.Client(
            api_key=self._config.api_key.get_secret_value(),
        )

    def generate(
        self, url: str, html_content: str, temperature: float = 0.0
    ) -> WordlistResponse:
        response = self._client.models.generate_content(
            model=self._config.model_name,
            contents=types.Content(
                role="user",
                parts=[types.Part(text=f"URL: {url}\n\nContent:\n{html_content}")],
            ),
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=GENERATOR_PROMPT,
                response_mime_type="application/json",
                response_schema=WordlistResponse,
            ),
        )

        if response.text is None:
            raise EmptyResponseTextError("Model did not generate any enpoints")
        return WordlistResponse.model_validate_json(response.text)
