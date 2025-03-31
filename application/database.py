import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import sessionmaker, DeclarativeBase

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
    disabled = Column(Boolean, nullable="True")


class Event(Base):
    __tablename__ = "event_info"
    title = Column(String, nullable="False")
    description = Column(String, nullable="False")
    start_date = Column(Date, nullable="False")
    end_date = Column(Date, nullable="False")
    location = Column(String, nullable="False")

class Speaker(Base):
    __tablename__ = "speaker_info"
    name = Column(String, nullable="False")
    bio = Column(String, nullable="False")
    contact_info = Column(String, nullable="False")

Base.metadata.create_all(engine)
