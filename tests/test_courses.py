from httpx import AsyncClient
from psu_course_review import models
import pytest


@pytest.mark.asyncio
async def test_no_permission_create_courses(
    client: AsyncClient,
    user1: models.DBUser,
):
    payload = {
        "course_name": "This is a course",
        "course_code": "123456",
        "course_description": "This is a course",
        "user_id": user1.id,
    }
    response = await client.post("/courses", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_permission_update_courses(
    client: AsyncClient,
    course_user1: models.DBCourse,
    user1: models.DBUser,
):
    payload = {
        "course_name": "This is a course",
        "course_code": "123456",
        "course_description": "This is a course",
        "user_id": user1.id,
    }
    response = await client.put(f"/courses/{course_user1.id}", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_permission_delete_courses(
    client: AsyncClient,
    course_user1: models.DBCourse,
):
    response = await client.delete(f"/courses/{course_user1.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_course(
    client: AsyncClient,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "course_name": "name",
        "course_code": "240-123",
        "course_description": "description",
        "user_id": token_user1.user_id,
    }
    response = await client.post("/courses", json=payload, headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] > 0
    assert data["course_code"] == payload["course_code"]
    assert data["course_name"] == payload["course_name"]
    assert data["course_description"] == payload["course_description"]
    assert data["review_posts_amount"] == 0
    assert data["user_id"] == token_user1.user_id


@pytest.mark.asyncio
async def test_update_course(
    client: AsyncClient,
    course_user1: models.DBCourse,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "course_name": "test course name",
        "course_code": "123-456",
        "course_description": "test description",
    }
    response = await client.put(
        f"/courses/{course_user1.id}", json=payload, headers=headers
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == course_user1.id
    assert data["course_code"] == payload["course_code"]
    assert data["course_name"] == payload["course_name"]
    assert data["course_description"] == payload["course_description"]


@pytest.mark.asyncio
async def test_update_other_user_course(
    client: AsyncClient,
    course_user1: models.DBCourse,
    token_user2: models.Token,
):
    headers = {"Authorization": f"{token_user2.token_type} {token_user2.access_token}"}
    payload = {
        "course_name": "name",
        "course_code": "240-123",
        "course_description": "description",
    }
    response = await client.put(
        f"/courses/{course_user1.id}", json=payload, headers=headers
    )
    data = response.json()

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_course(
    client: AsyncClient,
    course_user1: models.DBCourse,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    response = await client.delete(f"/courses/{course_user1.id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Course deleted"}


@pytest.mark.asyncio
async def test_delete_other_user_course(
    client: AsyncClient,
    course_user1: models.DBCourse,
    token_user2: models.Token,
):
    headers = {"Authorization": f"{token_user2.token_type} {token_user2.access_token}"}
    response = await client.delete(f"/courses/{course_user1.id}", headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_courses(
    client: AsyncClient,
    course_user1: models.DBCourse,
):
    response = await client.get("/courses")
    data = response.json()

    assert response.status_code == 200
    assert len(data["courses"]) > 0
    cheack_course = None

    for course in data["courses"]:
        if course["course_name"] == course_user1.course_name:
            cheack_course = course
            break

    assert cheack_course["id"] == course_user1.id
    assert cheack_course["course_name"] == course_user1.course_name
    assert cheack_course["course_code"] == course_user1.course_code
    assert cheack_course["course_description"] == course_user1.course_description
    assert cheack_course["review_posts_amount"] == course_user1.review_posts_amount
    assert cheack_course["user_id"] == course_user1.user_id


@pytest.mark.asyncio
async def test_review_posts_amount_field_of_course_increase_and_decrease(
    client: AsyncClient,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    # -------------------------review_posts_amount field of course increase testing--------------------------
    course_payload = {
        "course_name": "name",
        "course_code": "240-123",
        "course_description": "description",
        "user_id": token_user1.user_id,
    }
    response = await client.post("/courses", json=course_payload, headers=headers)
    course_data = response.json()
    assert response.status_code == 200
    assert course_data["review_posts_amount"] == 0

    review_post_payload = {
        "review_post_title": "This is a review post",
        "review_post_text": "This is a review post",
        "course_id": course_data["id"],
        "user_id": token_user1.user_id,
    }
    response = await client.post(
        "/review_posts", json=review_post_payload, headers=headers
    )
    review_post_data = response.json()
    assert response.status_code == 200

    response = await client.get(f"/courses/{course_data['id']}")
    course_data = response.json()
    assert response.status_code == 200
    assert course_data["review_posts_amount"] == 1
    # ------------------------------------------------------------------------------------------------------

    # -------------------------review_posts_amount field of course decrease testing--------------------------
    response = await client.delete(
        f"/review_posts/{review_post_data['id']}", headers=headers
    )
    assert response.status_code == 200

    response = await client.get(f"/courses/{course_data['id']}")
    course_data = response.json()
    assert response.status_code == 200
    assert course_data["review_posts_amount"] == 0
    # ------------------------------------------------------------------------------------------------------
