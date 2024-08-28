from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models

router = APIRouter(prefix="/review_posts", tags=["review_posts"])


SIZE_PER_PAGE = 50


@router.post("")
async def create_reviewpost(
    reviewpost: models.CreatedReviewPost,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ReviewPost:
    db_reviewpost = models.DBReviewPost.model_validate(reviewpost)
    session.add(db_reviewpost)
    await session.commit()
    await session.refresh(db_reviewpost)

    return models.ReviewPost.model_validate(db_reviewpost)

@router.get("")
async def read_reviewposts(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.ReviewPostList:
    query = (
        select(models.DBReviewPost).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    result = await session.exec(query)
    reviewposts = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBReviewPost.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return models.ReviewPostList.model_validate(
        dict(
            reviewposts=reviewposts,
            page_count=page_count,
            page=page,
            size_per_page=SIZE_PER_PAGE,
        )
    )

@router.get("/{reviewpost_id}")
async def read_reviewpost(
    reviewpost_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ReviewPost:
    db_reviewpost = await session.get(models.DBReviewPost, reviewpost_id)
    if db_reviewpost is None:
        raise HTTPException(status_code=404, detail="reviewpost not found")
    return models.ReviewPost.model_validate(db_reviewpost)


@router.put("/{reviewpost_id}")
async def update_reviewpost(
    reviewpost_id: int,
    reviewpost: models.UpdatedReviewPost,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ReviewPost:
    data = reviewpost.model_dump()
    db_reviewpost = await session.get(models.DBReviewPost, reviewpost_id)
    if db_reviewpost is None:
        raise HTTPException(status_code=404, detail="ReviewPost not found")

    db_reviewpost.sqlmodel_update(data)

    session.add(db_reviewpost)
    await session.commit()
    await session.refresh(db_reviewpost)

    return models.ReviewPost.model_validate(db_reviewpost)

@router.delete("/{reviewpost_id}")
async def delete_reviewpost(
    reviewpost_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_reviewpost = await session.get(models.DBReviewPost, reviewpost_id)
    if db_reviewpost is None:
        raise HTTPException(status_code=404, detail="ReviewPost not found")

    await session.delete(db_reviewpost)
    await session.commit()

    return dict(message="ReviewPost deleted")