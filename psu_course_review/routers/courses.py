from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/courses", tags=["courses"])


SIZE_PER_PAGE = 50


@router.post("")
async def create_course(
    course: models.CreatedCourse,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> models.Course:
    db_course = models.DBCourse.model_validate(course)

    db_course.user = current_user

    session.add(db_course)
    await session.commit()
    await session.refresh(db_course)

    return models.Course.model_validate(db_course)


@router.get("")
async def read_courses(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.CourseList:
    query = (
        select(models.DBCourse).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    result = await session.exec(query)
    courses = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBCourse.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return models.CourseList.model_validate(
        dict(
            courses=courses,
            page_count=page_count,
            page=page,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/{course_id}")
async def read_course(
    course_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Course:
    db_course = await session.get(models.DBCourse, course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return models.Course.model_validate(db_course)


@router.put("/{course_id}")
async def update_course(
    course_id: int,
    course: models.UpdatedCourse,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> models.Course:
    db_course = await session.get(models.DBCourse, course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if db_course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    course.review_posts_amount = db_course.review_posts_amount
    course.user_id = db_course.user_id

    data = course.model_dump()

    db_course.sqlmodel_update(data)

    session.add(db_course)
    await session.commit()
    await session.refresh(db_course)

    return models.Course.model_validate(db_course)


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> dict:
    db_course = await session.get(models.DBCourse, course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if db_course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await session.delete(db_course)
    await session.commit()

    return dict(message="Course deleted")
