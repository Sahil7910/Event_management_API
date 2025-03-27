

from models import Event, Attendee, EventStatus
from main import register_attendee, update_event_status
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from main import app, get_db
from models import Base, Event, Attendee
from auth import create_access_token
from time import sleep

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def db():
    """Creates a fresh database for each test."""
    Base.metadata.drop_all(bind=engine)  # Drop all tables (clears previous data)
    Base.metadata.create_all(bind=engine)  # Recreate tables

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Ensure test isolation
        db.close()

def get_test_token():
    """Generate a JWT token for testing."""
    test_user_data = {"sub": "testuser", "role": "admin"}  # Adjust according to your system
    return create_access_token(test_user_data, expires_delta=timedelta(hours=1))

def test_registration_limit(db: Session):


    db.query(Event).filter(Event.event_id == 1).delete()
    db.query(Attendee).filter(Attendee.event_id == 1).delete()
    db.commit()


    event = Event(
        event_id=1,
        name="Test Event",
        max_attendees=2,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(days=1),
        location="Test Venue",
        status=EventStatus.SCHEDULED
    )
    db.add(event)
    db.commit()
    db.refresh(event)


    db.add(Attendee(attendee_id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890", event_id=1))
    db.add(Attendee(attendee_id=2, first_name="Jane", last_name="Smith", email="jane@example.com", phone_number="1234567890", event_id=1))
    db.commit()


    with pytest.raises(Exception) as exc_info:
        register_attendee(1, Attendee(first_name="Mike", last_name="Brown", email="mike@example.com"), db)

    assert "Event is fully booked" in str(exc_info.value)




def test_successful_checkin(db: Session):
    """Creates an event and an attendee, then performs a successful check-in."""

    token = get_test_token()
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create Event
    event = Event(
        event_id=1,
        name="Python Meetup",
        description="test",
        location="Pune",
        max_attendees=50,
        start_time=datetime.utcnow() - timedelta(hours=2),
        end_time=datetime.utcnow() + timedelta(hours=1),
        status=EventStatus.SCHEDULED
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Create Attendee
    attendee = Attendee(
        attendee_id=1,
        first_name="Sahil",
        last_name="Kinjalkar",
        email="sahil@example.com",
        phone_number="9876543210",
        event_id=event.event_id,
        check_in_status=False
    )
    db.add(attendee)
    db.commit()
    db.refresh(attendee)

    # Perform Check-in
    response = client.put(
        f"/attendees/checkin/{attendee.attendee_id}/",
        headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Attendee checked in successfully"


    db.expire_all()


    updated_attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee.attendee_id).first()
    assert updated_attendee.check_in_status is True




def test_event_status_updates(db: Session):


    # Create an event that is currently scheduled
    event = Event(
        event_id=1,
        name="AI Conference",
        description="Tech event on AI advancements",
        location="Mumbai",
        max_attendees=100,
        start_time=datetime.utcnow() + timedelta(seconds=2),  # Starts in 2 seconds
        end_time=datetime.utcnow() + timedelta(seconds=5),    # Ends in 5 seconds
        status=EventStatus.SCHEDULED
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Ensure initial status is "SCHEDULED"
    assert event.status == EventStatus.SCHEDULED


    sleep(3)
    update_event_status(db)
    db.expire_all()

    # Fetch updated event
    updated_event = db.query(Event).filter(Event.event_id == event.event_id).first()
    assert updated_event.status == EventStatus.ONGOING


    sleep(3)
    update_event_status(db)
    db.expire_all()

    # Fetch updated event again
    updated_event = db.query(Event).filter(Event.event_id == event.event_id).first()
    assert updated_event.status == EventStatus.COMPLETED  # Should be COMPLETED now
