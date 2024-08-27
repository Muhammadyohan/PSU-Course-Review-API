from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models

router = APIRouter(prefix="/comments", tags=["comments"])


SIZE_PER_PAGE = 50


@router.post("")
async def create_comment(
    comment: models.CreatedComment,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Comment:
    db_comment = models.DBComment.model_validate(comment)
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
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Comment:
    data = comment.model_dump()
    db_comment = await session.get(models.DBComment, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    db_comment.sqlmodel_update(data)

    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)

    return models.Comment.model_validate(db_comment)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_comment = await session.get(models.DBComment, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    await session.delete(db_comment)
    await session.commit()

    return dict(message="Comment deleted")
