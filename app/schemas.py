from pydantic import BaseModel, Field


class PromptRequest(BaseModel):

    story_prompt: str = Field(
        default="A young hero discovers a magical secret in a forest.",
        min_length=3,
        max_length=2000,
    )

    character_name: str = Field(
        default="Alex",
        min_length=1,
        max_length=80,
    )

    setting: str = Field(
        default="enchanted forest",
        min_length=1,
        max_length=200,
    )

    tone: str = Field(
        default="funny",
        min_length=1,
        max_length=50,
    )

    art_style: str = Field(
        default="comic book",
        min_length=1,
        max_length=100,
    )