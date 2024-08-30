from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/comments", tags=["comments"])


SIZE_PER_PAGE = 50


@router.post("")
async def create_comment(
    comment: models.CreatedComment,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Comment:
    db_review_post = await session.get(models.DBReviewPost, comment.review_post_id)
    if db_review_post is None:
        raise HTTPException(status_code=404, detail="Review post not found")

    db_review_post.comments_amount += 1

    session.add(db_review_post)

    db_comment = models.DBComment.model_validate(comment)

    db_comment.comment_author = current_user.first_name + " " + current_user.last_name

    db_comment.review_post = db_review_post
    db_comment.user = current_user

    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)

    return models.Comment.model_validate(db_comment)


@router.get("")
async def read_comments(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.CommentList:
    query = (
        select(models.DBComment).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    result = await session.exec(query)
    comments = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBComment.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return models.CommentList.model_validate(
        dict(
            comments=comments,
            page_count=page_count,
            page=page,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/review_post/{review_post_id}")
async def read_comments_list_by_review_post_id(
    review_post_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.CommentList:
    query = (
        select(models.DBComment)
        .where(models.DBComment.review_post_id == review_post_id)
        .offset((page - 1) * SIZE_PER_PAGE)
        .limit(SIZE_PER_PAGE)
    )
    result = await session.exec(query)
    comments = result.all()

    page_count = int(
        math.ceil(
            (
                await session.exec(
                    select(func.count(models.DBComment.id)).where(
                        models.DBComment.review_post_id == review_post_id
                    )
                )
            ).first()
            / SIZE_PER_PAGE
        )
    )

    return models.CommentList.model_validate(
        dict(
            comments=comments,
            page_count=page_count,
            page=page,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/{comment_id}")
async def read_comment(
    comment_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Comment:
    db_comment = await session.get(models.DBComment, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    return models.Comment.model_validate(db_comment)


@router.put("/{comment_id}")
async def update_comment(
    comment_id: int,
    comment: models.UpdatedComment,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Comment:
    db_comment = await session.get(models.DBComment, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Forbidden, you are not the author of this comment"
        )

    comment.comment_author = db_comment.comment_author
    comment.review_post_id = db_comment.review_post_id
    comment.user_id = db_comment.user_id

    data = comment.model_dump()

    db_comment.sqlmodel_update(data)

    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)

    return models.Comment.model_validate(db_comment)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> dict:
    db_comment = await session.get(models.DBComment, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Forbidden, you are not the author of this comment"
        )

    db_review_post = await session.get(models.DBReviewPost, db_comment.review_post_id)
    db_review_post.comments_amount -= 1

    session.add(db_review_post)

    await session.delete(db_comment)
    await session.commit()
    await session.refresh(db_review_post)

    return dict(message="Comment deleted")
