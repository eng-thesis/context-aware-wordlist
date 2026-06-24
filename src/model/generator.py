from concurrent.futures import ThreadPoolExecutor, as_completed

from google.genai.errors import ServerError
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_groq import ChatGroq

from common.logging import get_logger
from model.config import GeneratorConfig
from model.models import WordlistResponse
from model.prompt import GENERATOR_PROMPT

log = get_logger(__name__)


class WordlistGenerator:
    def __init__(self, config: GeneratorConfig) -> None:
        self._config = config
        self._gemini = ChatGoogleGenerativeAI(
            model=self._config.gemini.model_name,
            google_api_key=self._config.gemini.api_key,
        ).with_structured_output(WordlistResponse)
        self._groq = ChatGroq(
            model=self._config.groq.model_name,
            api_key=self._config.groq.api_key,
        ).with_structured_output(WordlistResponse, method="json_schema", strict=True)

    def generate_multiple(
        self, url: str, html_content: str, temperature: float = 1.0, n: int = 5
    ) -> list[WordlistResponse]:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = [
                executor.submit(self.generate, url, html_content, temperature)
                for _ in range(n)
            ]
            return [f.result() for f in as_completed(futures)]

    def generate(
        self, url: str, html_content: str, temperature: float = 1.0
    ) -> WordlistResponse:
        try:
            return self._generate_gemini(url, html_content, temperature)
        except (ChatGoogleGenerativeAIError, ServerError) as e:
            log.warning(
                f"Google Gemini generation failed, falling back to Groq. Reason: {e}"
            )
            return self._generate_groq(url, html_content, temperature)

    def _invoke(
        self, llm: Runnable, url: str, html_content: str, temperature: float
    ) -> WordlistResponse:
        return llm.bind(temperature=temperature).invoke(
            [
                SystemMessage(content=GENERATOR_PROMPT),
                HumanMessage(content=f"URL: {url}\n\nContent:\n{html_content}"),
            ]
        )

    def _generate_gemini(
        self, url: str, html_content: str, temperature: float = 1.0
    ) -> WordlistResponse:
        return self._invoke(self._gemini, url, html_content, temperature)

    def _generate_groq(
        self, url: str, html_content: str, temperature: float = 1.0
    ) -> WordlistResponse:
        return self._invoke(self._groq, url, html_content, temperature)
