from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from database.models import NewsModel
from database.db import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
@router.get("/news/{news_id}", summary='Get news by id')
async def get_news(news_id: int, session: SessionDep):
    query = select(NewsModel).where(NewsModel.id == news_id)
    result = await session.execute(query)
    news = result.scalars().one_or_none()
    if news:
        return news
    else:
        raise HTTPException(status_code=404, detail="News not found")