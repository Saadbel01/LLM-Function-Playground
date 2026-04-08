from pydantic import BaseModel, Field
from typing import Literal, Union


class Parameter(BaseModel):
    type: Literal["number", "string", "boolean"]


class FunctionDefinition(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, Parameter]
    returns: Parameter


class TestPrompt(BaseModel):
    prompt: str = Field(min_length=1)


class FunctionCall(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, Union[float, str, bool]]
