from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.db.session import get_session
from apps.api.models import User
from apps.api.models.enums import PlanTierEnum, StatusEnum

router = APIRouter(prefix="/auth", tags=["auth"])


class DevLoginRequest(BaseModel):
    email: EmailStr


@router.post("/dev-login")
def dev_login(payload: DevLoginRequest, session: Session = Depends(get_session)) -> dict[str, str]:
    stmt = select(User).where(User.email == payload.email)
    user = session.scalar(stmt)
    if user is None:
        user = User(email=payload.email, plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
        session.add(user)
        session.flush()
    session.commit()
    return {"user_id": str(user.id), "email": user.email}
