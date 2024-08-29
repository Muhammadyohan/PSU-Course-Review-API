import sys
from pathlib import Path

# Add the parent directory of 'digital_wallet' to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport


from pydantic_settings import SettingsConfigDict

from psu_course_review import models, config, main, security

import pytest
import pytest_asyncio

import pathlib

import datetime


SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.recreate_table())

    yield app


@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:

    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user

    user = models.DBUser(
        email="test@test.com",
        username=username,
        first_name="Firstname",
        last_name="lastname",
        password=password,
        last_login_date=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    await user.set_password(password)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> dict:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user1
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user.last_login_date,
        user_id=user.id,
    )


@pytest_asyncio.fixture(name="course_user1")
async def example_course_user1(
    session: models.AsyncSession,
    user1: models.DBUser,
) -> models.DBCourse:
    course_name = "This is a course"
    course_code = "123456"
    course_description = "This is a course"

    query = await session.exec(
        models.select(models.DBCourse)
        .where(
            models.DBCourse.course_code == course_code,
            models.DBCourse.user_id == user1.id,
        )
        .limit(1)
    )
    course = query.one_or_none()
    if course:
        return course

    course = models.DBCourse(
        course_name=course_name,
        course_code=course_code,
        course_description=course_description,
        user=user1,
    )

    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


@pytest_asyncio.fixture(name="review_post_user1")
async def example_review_post_user1(
    session: models.AsyncSession,
    user1: models.DBUser,
    course_user1: models.DBCourse,
) -> models.DBReviewPost:
    review_post_title = "This is a review post"
    review_post_text = "This is a review post"
    likes_amount = 5

    query = await session.exec(
        models.select(models.DBReviewPost)
        .where(
            models.DBReviewPost.review_post_title == review_post_title,
            models.DBReviewPost.user_id == user1.id,
        )
        .limit(1)
    )
    review_post = query.one_or_none()
    if review_post:
        return review_post

    review_post = models.DBReviewPost(
        review_post_title=review_post_title,
        review_post_text=review_post_text,
        likes_amount=likes_amount,
        user=user1,
        course=course_user1,
    )

    session.add(review_post)
    await session.commit()
    await session.refresh(review_post)
    return review_post


@pytest_asyncio.fixture(name="comment_user1")
async def example_comment_user1(
    session: models.AsyncSession,
    user1: models.DBUser,
    review_post_user1: models.DBReviewPost,
) -> models.DBComment:
    comment_text = "This is a comment"
    comment_author = user1.first_name + " " + user1.last_name
    likes_amount = 5

    query = await session.exec(
        models.select(models.DBComment)
        .where(
            models.DBComment.comment_author == comment_author,
            models.DBComment.user_id == user1.id,
        )
        .limit(1)
    )
    comment = query.one_or_none()
    if comment:
        return comment

    comment = models.DBComment(
        comment_text=comment_text,
        comment_author=comment_author,
        likes_amount=likes_amount,
        review_post_id=review_post_user1.id,
        user=user1,
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment
