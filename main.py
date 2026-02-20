
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import List, Optional
import os
from dotenv import load_dotenv

# 1. Setup & Database Connection
load_dotenv()
app = FastAPI(title="Event Management System")

# Get MONGO_URI from .env safely
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.event_manager_db

# --- Helper to convert MongoDB ID to String ---
def format_doc(doc):
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

# --- 2. Data Models (Schemas) ---
class Event(BaseModel):
    name: str
    description: str
    date: str  # Format: YYYY-MM-DD
    venue: str
    maxParticipants: int = Field(gt=0)

class Participant(BaseModel):
    name: str
    email: EmailStr
    eventId: str

# --- 3. Event Routes ---

@app.post("/events", status_code=201)
async def create_event(event: Event):
    new_event = await db.events.insert_one(event.dict())
    return {"id": str(new_event.inserted_id)}

@app.get("/events", response_model=List[dict])
async def view_all_events(keyword: Optional[str] = None):
    # Bonus: Search by keyword
    query = {}
    if keyword:
        query = {"name": {"$regex": keyword, "$options": "i"}}
    
    events = await db.events.find(query).to_list(100)
    return [format_doc(e) for e in events]

@app.put("/events/{event_id}")
async def update_event(event_id: str, updated_data: Event):
    result = await db.events.replace_one({"_id": ObjectId(event_id)}, updated_data.dict())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event updated successfully"}

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    # Also delete registrations for this event to keep DB clean
    await db.registrations.delete_many({"eventId": event_id})
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event and its registrations deleted"}

# --- 4. Registration Routes ---

@app.post("/register")
async def register_participant(p: Participant):
    # Validate Event Existence
    event = await db.events.find_one({"_id": ObjectId(p.eventId)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Constraint: Enforce capacity limit
    count = await db.registrations.count_documents({"eventId": p.eventId})
    if count >= event["maxParticipants"]:
        raise HTTPException(status_code=400, detail="Event is full")

    # Constraint: Prevent duplicate registration
    duplicate = await db.registrations.find_one({"email": p.email, "eventId": p.eventId})
    if duplicate:
        raise HTTPException(status_code=400, detail="Already registered for this event")

    new_reg = await db.registrations.insert_one(p.dict())
    return {"registration_id": str(new_reg.inserted_id)}

@app.get("/events/{event_id}/participants")
async def view_participants(event_id: str):
    parts = await db.registrations.find({"eventId": event_id}).to_list(100)
    return [format_doc(p) for p in parts]

@app.delete("/registrations/{reg_id}")
async def delete_registration(reg_id: str):
    result = await db.registrations.delete_one({"_id": ObjectId(reg_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"message": "Registration deleted, seat freed"}

# --- 5. Bonus: Statistics ---

@app.get("/stats")
async def get_stats():
    total_events = await db.events.count_documents({})
    total_regs = await db.registrations.count_documents({})
    
    # Find most popular event
    pipeline = [
        {"$group": {"_id": "$eventId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    popular = await db.registrations.aggregate(pipeline).to_list(1)
    
    popular_event_name = "N/A"
    if popular:
        event = await db.events.find_one({"_id": ObjectId(popular[0]["_id"])})
        popular_event_name = event["name"] if event else "Unknown"

    return {
        "total_events": total_events,
        "total_registrations": total_regs,
        "most_popular_event": popular_event_name
    }
