from datetime import date
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
import re
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, User, Event, Speaker, Session, Participant, Budget
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from web.app import security

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        pass

class BaseModelScheme(BaseModel):
    id: int

class UserScheme(BaseModelScheme):
    username: str
    email: str
    full_name: str
    is_admin: bool

class EventScheme(BaseModelScheme):
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    organizer_id: int

class SpeakerScheme(BaseModelScheme):
    name: str
    bio: str
    contact_info: str

class SessionScheme(BaseModelScheme):
    event_id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    speaker_id: int

class ParticipantScheme(BaseModelScheme):
    event_id: int
    name: str
    email: str
    registration_date: datetime
    payment_status: bool

class BudgetItemScheme(BaseModelScheme):
    event_id: int
    name: str
    amount: float
    category: str
    is_expense: bool

# Валидация User
async def get_current_user(
    db: SessionLocal = Depends(get_db),
    user_id: int = Depends(security.access_token_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
