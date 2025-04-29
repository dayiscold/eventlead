# app.py
import os
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from authx import AuthXConfig, AuthX
from datetime import timedelta
from application.crud import (
    UserCreate, UserRead, UserUpdate,
    EventCreate, EventRead, EventUpdate,
    SpeakerCreate, SpeakerRead,
    SessionCreate, SessionRead,
    ParticipantCreate, ParticipantRead,
    BudgetCreate, BudgetRead
)
from application.database import SessionLocal, get_db, User, Event,  Speaker, Session, Participant, Budget
from passlib.context import CryptContext

app = FastAPI()

# AuthX Configuration
config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("SECRET_KEY", "secret")
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False


security = AuthX(config=config)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get current user
async def get_current_user(
        db: SessionLocal = Depends(get_db),
        user_id: int = Depends(security.access_token_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Auth Routes
@app.post("/auth/register", response_model=UserRead, tags=["Auth"])
async def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", tags=["Auth"])
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: SessionLocal = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/auth/refresh")
async def refresh(
    user_id: int = Depends(security.refresh_token_required),
):
    try:
        # Явное преобразование в строку и создание токена
        new_access_token = security.create_access_token(uid=str(user_id))
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/auth/logout", tags=["Auth"])
async def logout():
    response = Response(
        content='{"message": "Successfully logged out"}',
        media_type="application/json"
    )

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return response

# User Routes
@app.get("/users/me", response_model=UserRead, tags=["Users"])
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/users/me", response_model=UserRead, tags=["Users"])
async def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    for var, value in vars(user_update).items():
        if value is not None:
            setattr(current_user, var, value)
    db.commit()
    db.refresh(current_user)
    return current_user


# Event Routes
@app.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED, tags=["Events"])
async def create_event(
        event: EventCreate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    db_event = Event(**event.model_dump(), organizer_id=current_user.id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/events", response_model=list[EventRead], tags=["Events"])
async def read_events(
        skip: int = 0,
        limit: int = 100,
        db: SessionLocal = Depends(get_db)
):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events


@app.get("/events/{event_id}", response_model=EventRead, tags=["Events"])
async def read_event(event_id: int, db: SessionLocal = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.put("/events/{event_id}", response_model=EventRead, tags=["Events"])
async def update_event(
        event_id: int,
        event_update: EventUpdate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    if db_event.organizer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this event")

    for var, value in vars(event_update).items():
        if value is not None:
            setattr(db_event, var, value)

    db.commit()
    db.refresh(db_event)
    return db_event


@app.delete("/events/{event_id}", tags=["Events"])
async def delete_event(
        event_id: int,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    if db_event.organizer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")

    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted successfully"}


# Speaker Routes
@app.post("/speakers", response_model=SpeakerRead, status_code=status.HTTP_201_CREATED, tags=["Speakers"])
async def create_speaker(
        speaker: SpeakerCreate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    db_speaker = Speaker(**speaker.model_dump())
    db.add(db_speaker)
    db.commit()
    db.refresh(db_speaker)
    return db_speaker


# Session Routes
@app.post("/sessions", response_model=SessionRead, status_code=status.HTTP_201_CREATED, tags=["Sessions"])
async def create_session(
        session: SessionCreate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    # Verify event exists and user is organizer
    event = db.query(Event).filter(Event.id == session.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to add sessions to this event")

    db_session = Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


# Participant Routes
@app.post("/participants", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED, tags=["Participiants"])
async def create_participant(
        participant: ParticipantCreate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    # Verify event exists
    event = db.query(Event).filter(Event.id == participant.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_participant = Participant(**participant.model_dump(), user_id=current_user.id)
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


# Budget Routes
@app.post("/budgets", response_model=BudgetRead, status_code=status.HTTP_201_CREATED, tags=["Budgets"])
async def create_budget(
        budget: BudgetCreate,
        current_user: User = Depends(get_current_user),
        db: SessionLocal = Depends(get_db)
):
    # Verify event exists and user is organizer
    event = db.query(Event).filter(Event.id == budget.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to manage budgets for this event")

    db_budget = Budget(**budget.model_dump())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.get("/", tags=["Main"])
async def root():
    return {"message": "Event Management Platform API"}