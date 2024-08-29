from httpx import AsyncClient
from psu_course_review import models
import pytest


@pytest.mark.asyncio
async def test_create_review_post(
    client: AsyncClient,
    course_user1: models.DBCourse,
    token_user1: models.Token,
    user1: models.DBUser,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "review_post_title": "This is a review post",
        "review_post_text": "This is a review post",
        "course_id": course_user1.id,
        "user_id": token_user1.user_id,
    }
    response = await client.post("/review_posts", json=payload, headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] > 0
    assert data["review_post_title"] == payload["review_post_title"]
    assert data["review_post_text"] == payload["review_post_text"]
    assert data["author_name"] == user1.first_name + " " + user1.last_name
    assert data["likes_amount"] == 0
    assert data["comments_amount"] == 0
    assert data["course_code"] == course_user1.course_code
    assert data["course_name"] == course_user1.course_name
    assert data["course_id"] == course_user1.id
    assert data["user_id"] == token_user1.user_id


@pytest.mark.asyncio
async def test_update_review_post(
    client: AsyncClient,
    course_user1: models.DBCourse,
    review_post_user1: models.DBReviewPost,
    token_user1: models.Token,
    user1: models.DBUser,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "review_post_title": "This is a test review post",
        "review_post_text": "This is a test review post",
        "likes_amount": 5,
    }
    response = await client.put(
        f"/review_posts/{review_post_user1.id}", json=payload, headers=headers
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == review_post_user1.id
    assert data["review_post_title"] == payload["review_post_title"]
    assert data["review_post_text"] == payload["review_post_text"]
    assert data["likes_amount"] == payload["likes_amount"]


@pytest.mark.asyncio
async def test_delete_review_post(
    client: AsyncClient,
    review_post_user1: models.DBReviewPost,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(
        f"/review_posts/{review_post_user1.id}", headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Review Post deleted"}


@pytest.mark.asyncio
async def test_list_review_posts(
    client: AsyncClient,
    review_post_user1: models.DBReviewPost,
):
    response = await client.get(f"/review_posts")
    data = response.json()

    assert response.status_code == 200
    assert len(data["review_posts"]) > 0
    check_review_post = None

    for review_post in data["review_posts"]:
        if review_post["id"] == review_post_user1.id:
            check_review_post = review_post
            break

    assert check_review_post["id"] == review_post_user1.id
    assert check_review_post["review_post_title"] == review_post_user1.review_post_title
    assert check_review_post["review_post_text"] == review_post_user1.review_post_text
    assert check_review_post["likes_amount"] == review_post_user1.likes_amount
    assert check_review_post["author_name"] == review_post_user1.author_name
    assert check_review_post["course_name"] == review_post_user1.course_name
    assert check_review_post["course_code"] == review_post_user1.course_code
    assert check_review_post["comments_amount"] == review_post_user1.comments_amount
    assert check_review_post["user_id"] == review_post_user1.user_id
