from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

import math

from .. import models
from .. import deps

router = APIRouter(prefix="/events", tags=["events"])

SIZE_PER_PAGE = 50


@router.post("")
async def create_event(
    event: models.CreatedEvent,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Event:
    db_event = models.DBEvent.model_validate(event)

    db_event.author_name = current_user.first_name + " " + current_user.last_name
    db_event.user = current_user

    session.add(db_event)
    await session.commit()
    await session.refresh(db_event)

    return models.Event.model_validate(db_event)


@router.get("")
async def read_events(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> models.EventList:
    query = (
        select(models.DBEvent).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    result = await session.exec(query)
    events = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(models.DBEvent.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return models.EventList.model_validate(
        dict(
            events=events,
            page_count=page_count,
            page=page,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/{event_id}")
async def read_event(
    event_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Event:
    db_event = await session.get(models.DBEvent, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return models.Event.model_validate(db_event)


@router.put("/{event_id}")
async def update_event(
    event_id: int,
    event: models.UpdatedEvent,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> models.UpdatedEvent:
    db_event = await session.get(models.DBEvent, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if db_event.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You are not the owner of this event"
        )

    event.author_name = db_event.author_name
    event.user_id = db_event.user_id

    data = event.model_dump()

    db_event.sqlmodel_update(data)

    session.add(db_event)
    await session.commit()
    await session.refresh(db_event)

    return models.UpdatedEvent.model_validate(db_event)


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> dict:
    db_event = await session.get(models.DBEvent, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if db_event.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="You are the owner of this event")

    await session.delete(db_event)
    await session.commit()

    return dict(message="Event deleted")
