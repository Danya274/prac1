from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    pass


class NewsModel(Base):
    __tablename__ = 'news'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    text: Mapped[str]
    link: Mapped[str]
    date: Mapped[datetime] = mapped_column(DateTime)
