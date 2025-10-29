from pydantic import BaseModel
from typing import Any
from datetime import datetime

class DefaultResponse(BaseModel):
    error: bool
    message: str
    payload: Any | None = None


class NewsSchema(BaseModel):
    id: int
    title: str | None = None
    text: str | None = None
    link: str | None = None
    date: datetime | None = None