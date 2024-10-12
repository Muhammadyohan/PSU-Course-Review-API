from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

from . import users


class BaseReviewPost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_post_title: str
    review_post_text: str
    course_code: str
    course_name: str
    likes_amount: int = 0
    author_name: str | None = None
    comments_amount: int = 0
    user_id: int | None = 0


class CreatedReviewPost(BaseReviewPost):
    pass


class UpdatedReviewPost(BaseReviewPost):
    pass


class ReviewPost(BaseReviewPost):
    id: int


class DBReviewPost(BaseReviewPost, SQLModel, table=True):
    __tablename__ = "review_posts"
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()


class ReviewPostList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_posts: list[ReviewPost]
    page: int
    page_count: int
    size_per_page: int
