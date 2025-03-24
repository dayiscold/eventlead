from typing import Optional
from pydantic import BaseModel
from datetime import datetime



class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class Event(BaseModel):
    id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    organizer_id: int

class Session(BaseModel):
    id: int
    event_id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    speaker_id: int

class Speaker(BaseModel):
    id: int
    name: str
    bio: str
    contact_info: str

class Participant(BaseModel):
    id: int
    event_id: int
    name: str
    email: str
    registration_date: datetime
    payment_status: bool

class BudgetItem(BaseModel):
    id: int
    event_id: int
    name: str
    amount: float
    category: str
    is_expense: bool