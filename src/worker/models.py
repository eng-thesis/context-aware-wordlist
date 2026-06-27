from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


class WordlistTaskPayload(BaseModel):
    url: str = Field(description="URL of the webpage to generate wordlist for")
    html_content: str = Field(description="HTML content of the webpage")
    n: int = Field(default=3, description="Number of concurrent requests to send")

    # TODO: replace this with file_url when database for files is introduced
    input_wordlist: list[str] = Field(
        default_factory=list,
        description="Optional wordlist to merge with generated results",
    )


class WordlistTaskMetadata(BaseModel):
    correlation_id: str = Field(description="Correlation ID for tracking the task")


class WordlistTask(BaseModel):
    metadata: WordlistTaskMetadata
    payload: WordlistTaskPayload


class WordlistResultPayload(BaseModel):
    url: str = Field(description="URL of the webpage")
    endpoints: list[str] = Field(
        default_factory=list, description="Generated list of endpoints"
    )


class WordlistErrorPayload(BaseModel):
    error_message: str = Field(description="Error message")


class WordlistResultMetadata(BaseModel):
    correlation_id: str = Field(description="Correlation ID for tracking the task")
    status: TaskStatus = Field(description="Status of the task")


class WordlistResult(BaseModel):
    metadata: WordlistResultMetadata
    payload: WordlistResultPayload | WordlistErrorPayload
