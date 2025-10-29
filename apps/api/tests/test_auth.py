from __future__ import annotations

from http import HTTPStatus

from sqlalchemy import select

from apps.api.models import User


def test_dev_login_creates_user(client, db_session):
    payload = {"email": "login@example.com"}
    response = client.post("/auth/dev-login", json=payload)

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["email"] == "login@example.com"
    assert body["user_id"]

    user = db_session.execute(select(User).where(User.email == "login@example.com")).scalar_one()
    assert str(user.id) == body["user_id"]
