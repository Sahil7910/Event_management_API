from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Event, Attendee, EventStatus
from schemas import EventCreate, EventResponse, AttendeeCreate, AttendeeResponse
from auth import hash_password, verify_password, create_access_token, decode_access_token,get_current_user
import pandas as pd
from fastapi import UploadFile, File
from typing import List, Optional
from datetime import datetime

# Initialize FastAPI
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_event_status(db: Session):

    now = datetime.utcnow()
    events = db.query(Event).all()

    for event in events:
        if event.start_time <= now < event.end_time and event.status != EventStatus.ONGOING:
            event.status = EventStatus.ONGOING
        elif now >= event.end_time and event.status != EventStatus.COMPLETED:
            event.status = EventStatus.COMPLETED

    db.commit()


@app.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_event_status(event, db)

    return event



@app.post("/events/", dependencies=[Depends(get_current_user)], status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(**event.dict(), status=EventStatus.scheduled)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event



@app.put("/events/{event_id}/", dependencies=[Depends(get_current_user)])
def update_event(event_id: int, updated_event: EventCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for key, value in updated_event.dict().items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


@app.post("/events/attendees/{event_id}/", response_model=AttendeeResponse, dependencies=[Depends(get_current_user)])
def register_attendee(event_id: int, attendee: AttendeeCreate, db: Session = Depends(get_db)):
    # Check if event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check for duplicate email
    existing_attendee = db.query(Attendee).filter(Attendee.email == attendee.email, Attendee.event_id == event_id).first()
    if existing_attendee:
        raise HTTPException(status_code=400, detail="Attendee with this email is already registered for the event")

    # Check if event is fully booked
    attendee_count = db.query(Attendee).filter(Attendee.event_id == event_id).count()
    if attendee_count >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event is fully booked")

    # Create new attendee
    new_attendee = Attendee(**attendee.dict(), event_id=event_id)
    db.add(new_attendee)
    db.commit()
    db.refresh(new_attendee)

    return new_attendee



@app.put("/attendees/checkin/{attendee_id}/", dependencies=[Depends(get_current_user)])
def check_in_attendee(attendee_id: int, db: Session = Depends(get_db)):
    attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    attendee.check_in_status = True
    db.commit()
    return {"message": "Attendee checked in successfully"}



@app.get("/events/", dependencies=[Depends(get_current_user)])
def list_events(status: str = None, location: str = None, db: Session = Depends(get_db)):
    query = db.query(Event)

    if status:
        query = query.filter(Event.status == status)
    if location:
        query = query.filter(Event.location == location)

    return query.all()


@app.get("/events/attendees/{event_id}/", response_model=List[AttendeeResponse])
def list_attendees(
    event_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    check_in_status: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    # Check if event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")


    query = db.query(Attendee).filter(Attendee.event_id == event_id)


    if first_name:
        query = query.filter(Attendee.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Attendee.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Attendee.email.ilike(f"%{email}%"))
    if check_in_status is not None:
        query = query.filter(Attendee.check_in_status == check_in_status)

    return query.all()


@app.post("/register/")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(password)
    user = User(username=username, hashed_password=hashed_password)

    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}


# Login and Get JWT Token
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}



def get_current_user(token: str = Security(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["sub"]

@app.get("/protected/")
def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}! You have access to this protected route."}



@app.post("/events/{event_id}/bulk_checkin/", dependencies=[Depends(get_current_user)])
def bulk_checkin(event_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")


    df = pd.read_csv(file.file)

    # Ensure required column exists
    if "email" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain an 'email' column")


    checked_in_count = 0
    for email in df["email"]:
        attendee = db.query(Attendee).filter(Attendee.email == email, Attendee.event_id == event_id).first()
        if attendee and not attendee.check_in_status:
            attendee.check_in_status = True
            db.commit()
            checked_in_count += 1

    return {"message": f"{checked_in_count} attendees checked in successfully!"}

