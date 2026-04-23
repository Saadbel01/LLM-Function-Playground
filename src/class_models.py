from pydantic import BaseModel, Field
from typing import Literal, Union


class Parameter(BaseModel):
    """Describe a function parameter type."""
    type: Literal["number", "string", "boolean", "integer"]


class FunctionDefinition(BaseModel):
    """Represent a function specification used for calling."""
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, Parameter]
    returns: Parameter


class TestPrompt(BaseModel):
    """Represent a user prompt used in tests."""
    prompt: str = Field(min_length=1)


class FunctionCall(BaseModel):
    """Represent a generated function call output."""
    prompt: str
    name: str
    parameters: dict[str, Union[float, str, bool, int]]
