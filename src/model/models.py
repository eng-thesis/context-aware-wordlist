from pydantic import BaseModel, Field


class WordlistResponse(BaseModel):
    endpoints: list[str] = Field(
        default_factory=list, description="List of discovered endpoints"
    )
