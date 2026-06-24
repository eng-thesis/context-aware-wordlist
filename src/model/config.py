from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class GeminiConfig(BaseModel):
    api_key: SecretStr = Field(description="Gemini API key")
    model_name: str = Field(description="Gemini model name")


class GroqConfig(BaseModel):
    api_key: SecretStr = Field(description="Groq API key")
    model_name: str = Field(description="Groq model name")


class GeneratorConfig(BaseSettings):
    gemini: GeminiConfig
    groq: GroqConfig

    model_config = SettingsConfigDict(yaml_file="config.yaml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)
