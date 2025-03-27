from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Enum for Event Status
class EventStatus(enum.Enum):  # ✅ Correct way to define an Enum
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"


# Event Model
class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    max_attendees = Column(Integer, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.UPCOMING)

    attendees = relationship("Attendee", back_populates="event")  # Ensures `event.attendees` works


# Attendee Model
class Attendee(Base):
    __tablename__ = "attendees"

    attendee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    check_in_status = Column(Boolean, default=False)

    event = relationship("Event", back_populates="attendees")