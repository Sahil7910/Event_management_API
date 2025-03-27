from pydantic import BaseModel, EmailStr,ConfigDict
from datetime import datetime
from typing import Optional

# Schema for Event Creation
class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int

# Schema for Event Response
class EventResponse(EventCreate):
    event_id: int
    status: str

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)

# Schema for Attendee Registration
class AttendeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str

# Schema for Attendee Response
class AttendeeResponse(BaseModel):
    attendee_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    event_id: int

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)
