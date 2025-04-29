# crud.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserRead(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str
    start_date: datetime
    end_date: datetime
    location: str

    @field_validator('start_date', 'end_date')
    def ensure_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        return v

    @field_validator('end_date')
    def validate_end_date(cls, v: datetime, values) -> datetime:
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("End date must be after start date")
        return v

class EventCreate(EventBase):
    pass

class EventRead(EventBase):
    id: int
    organizer_id: int

    class Config:
        from_attributes = True

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None

class SpeakerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    bio: str
    contact_info: str

class SpeakerCreate(SpeakerBase):
    pass

class SpeakerRead(SpeakerBase):
    id: int

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    event_id: int
    speaker_id: int

    @field_validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError("End time must be after start time")
        return v

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int

    class Config:
        from_attributes = True

class ParticipantBase(BaseModel):
    name: str
    email: EmailStr
    event_id: int

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantRead(ParticipantBase):
    id: int
    registration_date: datetime
    payment_status: bool

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    category: str
    is_expense: bool
    event_id: int

class BudgetCreate(BudgetBase):
    pass

class BudgetRead(BudgetBase):
    id: int

    class Config:
        from_attributes = True