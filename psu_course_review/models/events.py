from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship

from . import users


class BaseEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_title: str
    event_description: str
    event_date: str
    likes_amount: int = 0
    author_name: str | None = None
    user_id: int | None = 0


class CreatedEvent(BaseEvent):
    pass


class UpdatedEvent(BaseEvent):
    pass


class Event(BaseEvent):
    id: int


class DBEvent(BaseEvent, SQLModel, table=True):
    __tablename__ = "events"
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship(cascade_delete=True)


class EventList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    events: list[Event]
    page: int
    page_count: int
    size_per_page: int
