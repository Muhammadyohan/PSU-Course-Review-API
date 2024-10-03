# from pydantic import BaseModel, ConfigDict
# from sqlmodel import SQLModel, Field, Relationship
# from typing import Optional

# from . import users


# class BaseCourse(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     course_code: str
#     course_name: str
#     course_description: str
#     review_posts_amount: int = 0
#     user_id: int | None = 0


# class CreatedCourse(BaseCourse):
#     pass


# class UpdatedCourse(BaseCourse):
#     pass


# class Course(BaseCourse):
#     id: int


# class DBCourse(BaseCourse, SQLModel, table=True):
#     __tablename__ = "courses"
#     id: Optional[int] = Field(default=None, primary_key=True)

#     user_id: int = Field(default=None, foreign_key="users.id")
#     user: users.DBUser | None = Relationship()


# class CourseList(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     courses: list[Course]
#     page: int
#     page_count: int
#     size_per_page: int
