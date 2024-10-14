from httpx import AsyncClient
from psu_course_review import models
import pytest


@pytest.mark.asyncio
async def test_no_permission_create_event(
    client: AsyncClient,
    user1: models.DBUser,
):
    payload = {
        "event_title": "This is a event",
        "event_description": "This is a event",
        "event_date": "30 Oct 2024",
        "category": "Sport",
        "user_id": user1.id,
    }
    response = await client.post("/events", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_permission_update_event(
    client: AsyncClient,
    event_user1: models.DBEvent,
):
    payload = {
        "event_title": "This is a event",
        "event_description": "This is a event",
        "event_date": "30 Oct 2024",
        "category": "Sport",
        "likes_amount": 5,
    }
    response = await client.put(f"/events/{event_user1.id}", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_no_permission_delete_event(
    client: AsyncClient,
    event_user1: models.DBEvent,
):
    response = await client.delete(f"/events/{event_user1.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_event(
    client: AsyncClient,
    token_user1: models.Token,
    user1: models.DBUser,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "event_title": "This is a review post",
        "event_description": "This is a review post",
        "event_date": "30 Oct 2024",
        "category": "Sport",
        "user_id": token_user1.user_id,
    }
    response = await client.post("/events", json=payload, headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] > 0
    assert data["event_title"] == payload["event_title"]
    assert data["event_description"] == payload["event_description"]
    assert data["event_date"] == payload["event_date"]
    assert data["category"] == payload["category"]
    assert data["likes_amount"] == 0
    assert data["author_name"] == user1.first_name + " " + user1.last_name
    assert data["user_id"] == token_user1.user_id


@pytest.mark.asyncio
async def test_update_event(
    client: AsyncClient,
    event_user1: models.DBEvent,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "event_title": "This is a event",
        "event_description": "This is a event",
        "event_date": "30 Oct 2024",
        "category": "Sport",
        "likes_amount": 5,
    }
    response = await client.put(
        f"/events/{event_user1.id}", json=payload, headers=headers
    )
    data = response.json()
    print(data)

    assert response.status_code == 200
    assert data["id"] == event_user1.id
    assert data["event_title"] == payload["event_title"]
    assert data["event_description"] == payload["event_description"]
    assert data["event_date"] == payload["event_date"]
    assert data["category"] == payload["category"]
    assert data["likes_amount"] == payload["likes_amount"]


@pytest.mark.asyncio
async def test_delete_event(
    client: AsyncClient,
    event_user1: models.DBEvent,
    token_user1: models.Token,
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(f"/events/{event_user1.id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Event deleted"}


@pytest.mark.asyncio
async def test_list_events(
    client: AsyncClient,
    event_user1: models.DBEvent,
):
    response = await client.get(f"/events")
    data = response.json()

    assert response.status_code == 200
    assert len(data["events"]) > 0
    check_event = None

    for event in data["events"]:
        if event["id"] == event_user1.id:
            check_event = event
            break

    assert check_event["id"] == event_user1.id
    assert check_event["event_title"] == event_user1.event_title
    assert check_event["event_description"] == event_user1.event_description
    assert check_event["event_date"] == event_user1.event_date
    assert check_event["category"] == event_user1.category
    assert check_event["likes_amount"] == event_user1.likes_amount
    assert check_event["author_name"] == event_user1.author_name
    assert check_event["user_id"] == event_user1.user_id
