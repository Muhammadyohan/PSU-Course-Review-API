from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/review_posts", tags=["review_posts"])


SIZE_PER_PAGE = 50


@router.post("")
async def create_review_post(
    review_post: models.CreatedReviewPost,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> models.ReviewPost:
    db_review_post = models.DBReviewPost.model_validate(review_post)

    db_review_post.author_name = current_user.first_name + " " + current_user.last_name
    db_review_post.user = current_user

    session.add(db_review_post)
    await session.commit()
    await session.refresh(db_review_post)

    return models.ReviewPost.model_validate(db_review_post)


@router.get("")
async def read_review_posts(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.ReviewPostList:
    query = (
        select(models.DBReviewPost)
        .offset((page - 1) * SIZE_PER_PAGE)
        .limit(SIZE_PER_PAGE)
    )
    result = await session.exec(query)
    review_posts = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBReviewPost.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return models.ReviewPostList.model_validate(
        dict(
            review_posts=review_posts,
            page_count=page_count,
            page=page,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/{review_post_id}")
async def read_review_post(
    review_post_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ReviewPost:
    db_review_post = await session.get(models.DBReviewPost, review_post_id)
    if db_review_post is None:
        raise HTTPException(status_code=404, detail="Review Post not found")

    return models.ReviewPost.model_validate(db_review_post)


@router.put("/{review_post_id}")
async def update_review_post(
    review_post_id: int,
    review_post: models.UpdatedReviewPost,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> models.ReviewPost:
    db_review_post = await session.get(models.DBReviewPost, review_post_id)
    if db_review_post is None:
        raise HTTPException(status_code=404, detail="Review Post not found")

    if db_review_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden, not your review post")

    review_post.author_name = db_review_post.author_name
    review_post.comments_amount = db_review_post.comments_amount
    review_post.user_id = db_review_post.user_id

    data = review_post.model_dump()

    db_review_post.sqlmodel_update(data)

    session.add(db_review_post)
    await session.commit()
    await session.refresh(db_review_post)

    return models.ReviewPost.model_validate(db_review_post)


@router.delete("/{review_post_id}")
async def delete_review_post(
    review_post_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> dict:
    db_review_post = await session.get(models.DBReviewPost, review_post_id)
    if db_review_post is None:
        raise HTTPException(status_code=404, detail="Review Post not found")

    if db_review_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden, not your review post")

    await session.delete(db_review_post)
    await session.commit()

    return dict(message="Review Post deleted")
