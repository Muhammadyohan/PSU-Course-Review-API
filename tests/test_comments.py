from httpx import AsyncClient
from psu_course_review import models
import pytest


@pytest.mark.asyncio
async def test_no_permission_create_comment(
    client: AsyncClient,
    user1: models.DBUser,
    review_post_user1: models.DBReviewPost,
):
    payload = {
        "comment_text": "This is a comment",
        "review_post_id": review_post_user1.id,
        "user_id": user1.id,
    }
    response = await client.post("/comments", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_permission_update_comment(
    client: AsyncClient,
    comment_user1: models.DBComment,
):
    payload = {
        "comment_text": "This is a comment",
        "likes_amount": 5,
    }
    response = await client.put(f"/comments/{comment_user1.id}", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_permission_delete_comment(
    client: AsyncClient,
    comment_user1: models.DBComment,
):
    response = await client.delete(f"/comments/{comment_user1.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_comment(
    client: AsyncClient,
    review_post_user1: models.DBReviewPost,
    token_user1: models.Token,
    user1: models.DBUser,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "comment_text": "This is a comment",
        "review_post_id": review_post_user1.id,
        "user_id": token_user1.user_id,
    }
    response = await client.post("/comments", json=payload, headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["id"] > 0
    assert data["comment_author"] == user1.first_name + " " + user1.last_name
    assert data["comment_text"] == payload["comment_text"]
    assert data["likes_amount"] == 0
    assert data["review_post_id"] == review_post_user1.id
    assert data["user_id"] == token_user1.user_id


@pytest.mark.asyncio
async def test_update_comment(
    client: AsyncClient,
    comment_user1: models.DBComment,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "comment_text": "test text",
        "likes_amount": 1,
    }
    response = await client.put(
        f"/comments/{comment_user1.id}", json=payload, headers=headers
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == comment_user1.id
    assert data["comment_text"] == payload["comment_text"]
    assert data["likes_amount"] == payload["likes_amount"]


@pytest.mark.asyncio
async def test_update_other_user_comment(
    client: AsyncClient,
    comment_user1: models.DBComment,
    token_user2: models.Token,
):
    headers = {"Authorization": f"{token_user2.token_type} {token_user2.access_token}"}
    payload = {
        "comment_text": "test text",
        "likes_amount": 1,
    }
    response = await client.put(
        f"/comments/{comment_user1.id}", json=payload, headers=headers
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment(
    client: AsyncClient,
    comment_user1: models.DBComment,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(f"/comments/{comment_user1.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted"


@pytest.mark.asyncio
async def test_delete_other_user_comment(
    client: AsyncClient,
    comment_user1: models.DBComment,
    token_user2: models.Token,
):
    headers = {"Authorization": f"{token_user2.token_type} {token_user2.access_token}"}

    response = await client.delete(f"/comments/{comment_user1.id}", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient, comment_user1: models.DBComment):
    response = await client.get("/comments")

    data = response.json()

    assert response.status_code == 200
    assert len(data["comments"]) > 0
    check_comment = None

    for comment in data["comments"]:
        if comment["comment_author"] == comment_user1.comment_author:
            check_comment = comment
            break

    assert check_comment["id"] == comment_user1.id
    assert check_comment["comment_author"] == comment_user1.comment_author
    assert check_comment["comment_text"] == comment_user1.comment_text
    assert check_comment["likes_amount"] == comment_user1.likes_amount
    assert check_comment["review_post_id"] == comment_user1.review_post_id
    assert check_comment["user_id"] == comment_user1.user_id
