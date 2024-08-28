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
    hash_password = security.get_password_hash(password)
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username,
        hashed_password=hash_password,
        email="test@test.com",
        telephone="0812345678",
        first_name="Firstname",
        last_name="lastname",
        disabled=False,
    )

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
        issued_at=datetime.datetime.now(),
        user_id=str(user.id),
    )


# @pytest_asyncio.fixture(name="review_post_user1")
# async def example_item_user1(
#     session: models.AsyncSession,
#     user1: models.DBUser,
# ) -> models.DBReviewPost:
#     title = "This is a review post"
#     author_name = "author_name"
#     post_text = "This is a review post"
#     likes_amount = 5
#     comments_amount = 5


@pytest_asyncio.fixture(name="comment_user1")
async def example_item_user1(
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
    item = query.one_or_none()
    if item:
        return item

    item = models.DBComment(
        comment_text=comment_text,
        comment_author=comment_author,
        likes_amount=likes_amount,
        review_post_id=review_post_user1.id,
        user=user1,
    )

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
