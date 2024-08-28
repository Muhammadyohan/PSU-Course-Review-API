from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class BaseReviewPost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reviewpost_header: str
    reviewpost_paragraph: str
    author_name: str
    likes_amount: int = 0
    course_id: int | None = 0
    course_code: str
    course_name: str
    user_id: int | None = 0


class CreatedReviewPost(BaseReviewPost):
    pass


class UpdatedReviewPost(BaseReviewPost):
    pass


class ReviewPost(BaseReviewPost):
    id: int


class DBReviewPost(BaseReviewPost, SQLModel, table=True):
    __tablename__ = "reviewposts"
    id: Optional[int] = Field(default=None, primary_key=True)

    # Wait for Review_Post Model to write the code below
    # review_post_id: int = Field(default=None, foreign_key="review_posts.id")
    # review_post: review_posts.DBReviewPost = Relationship()


    # Wait for User Model to write the code below
    # user_id: int = Field(default=None, foreign_key="users.id")
    # user: users.DBUser | None = Relationship()


class ReviewPostList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reviewposts: list[ReviewPost]
    page: int
    page_count: int
    size_per_page: int