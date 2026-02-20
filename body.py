from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Event Manager API")

# Database Connection
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client.event_db

# --- Models (Data Structures) ---
class Event(BaseModel):
    name: str
    description: str
    date: str
    venue: str
    maxParticipants: int

class Participant(BaseModel):
    name: str
    email: EmailStr
    eventId: str

# --- Routes ---

@app.get("/")
def home():
    return {"message": "Event API is running!"}

# 1. Create Event
@app.post("/events")
async def create_event(event: Event):
    new_event = await db.events.insert_one(event.dict())
    return {"id": str(new_event.inserted_id)}

# 2. View All Events
@app.get("/events")
async def get_events():
    events = await db.events.find().to_list(100)
    for e in events: e["_id"] = str(e["_id"])
    return events

# 3. Register Participant
@app.post("/register")
async def register(participant: Participant):
    # Check if event exists
    event = await db.events.find_one({"_id": ObjectId(participant.eventId)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check capacity
    current_count = await db.registrations.count_documents({"eventId": participant.eventId})
    if current_count >= event["maxParticipants"]:
        raise HTTPException(status_code=400, detail="Event is full!")

    # Check duplicate email for this event
    duplicate = await db.registrations.find_one({"email": participant.email, "eventId": participant.eventId})
    if duplicate:
        raise HTTPException(status_code=400, detail="User already registered for this event")

    await db.registrations.insert_one(participant.dict())
    return {"message": "Registration successful"}

# 4. View Participants of an Event
@app.get("/events/{event_id}/participants")
async def get_participants(event_id: str):
    parts = await db.registrations.find({"eventId": event_id}).to_list(100)
    for p in parts: p["_id"] = str(p["_id"])
    return parts