from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship

from . import users
from . import review_posts


class BaseComment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    comment_text: str
    comment_author: str | None = None
    likes_amount: int = 0
    review_post_id: int | None = 0
    user_id: int | None = 0


class CreatedComment(BaseComment):
    pass


class UpdatedComment(BaseComment):
    pass


class Comment(BaseComment):
    id: int


class DBComment(BaseComment, SQLModel, table=True):
    __tablename__ = "comments"
    id: Optional[int] = Field(default=None, primary_key=True)

    review_post_id: int = Field(default=None, foreign_key="review_posts.id")
    review_post: review_posts.DBReviewPost = Relationship()

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()


class CommentList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    comments: list[Comment]
    page: int
    page_count: int
    size_per_page: int
