from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.DATABASE_NAME]
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")

def get_collection(name: str):
    if db.db is None:
        raise Exception("Database not initialized. Please wait for startup or check connection.")
    return db.db[name]
