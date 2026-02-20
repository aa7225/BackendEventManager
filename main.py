import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
