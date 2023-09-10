from typing import NotRequired, TypedDict

class CompletionMessage(TypedDict):
    content: str
    role: str
    name: NotRequired[str]
