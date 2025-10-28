from pydantic import BaseModel
from typing import Any

class DefaultResponse(BaseModel):
    error: bool
    message: str
    payload: Any | None = None


class NewsSchema(BaseModel):
    id: int
    title: str | None = None
    text: str | None = None
    link: str | None = None
    date: str | None = None