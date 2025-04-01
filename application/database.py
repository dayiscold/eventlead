import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, re
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Relationship

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):  # noqa: E701
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


class User(Base):
    __tablename__ = "user_info"
    username = Column(String, nullable="False", unique=True)
    email = Column(String, unique=True)
    full_name = Column(String, nullable="True")
    is_admin = Column(Boolean, default=False)


class Event(Base):
    __tablename__ = "event_info"
    title = Column(String, nullable="False")
    description = Column(String, nullable="False")
    start_date = Column(Date, nullable="False")
    end_date = Column(Date, nullable="False")
    location = Column(String, nullable="True")
    creator_id = Column(Integer, ForeignKey("users.id"))
    sessions = Relationship("Session", backref="event")      # Связь с сессиями
    participants = Relationship("Participant", backref="event")  # Связь с участниками

class Speaker(Base):
    __tablename__ = "speaker_info"
    name = Column(String, nullable="False")
    bio = Column(String, nullable="False")
    contact_info = Column(String, nullable="False")

    sessions = Relationship("Session", backref="speaker")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    title = Column(String)
    time = Column(String)
    speaker_id = Column(Integer, ForeignKey("speakers.id"))


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    name = Column(String)
    email = Column(String)
    paid = Column(Boolean, default=False)


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    total = Column(Integer)
    spent = Column(Integer, default=0)

Base.metadata.create_all(engine)
