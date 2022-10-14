from pymongo.database import Database
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from app.utils import hash, verify
from app.config import settings



# Connect to the database

def get_db():
    client = MongoClient(f"mongodb+srv://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@cluster0.pnxofvu.mongodb.net/?retryWrites=true&w=majority")
    db = client.phishing_website_detection
    try:
        yield db
    finally:
        client.close()


def check_user_exists(item: dict, db: Database) -> bool:
    user = db.users.find_one({"email": item["email"]})
    if user and verify(item["password"], user["password"]):
        return user
    return None


# Database CRUD functions

def create_user(item: dict, db: Database) -> dict:
    if db.users.count_documents() > settings.USER_LIMIT:
        return "LIMIT"
    if db.users.count_documents({"email": item["email"]}):
        return None
    item["password"] = hash(item["password"])
    item.update({"created_at": datetime.utcnow()})
    id = db.users.insert_one(item).inserted_id
    db.users.update_one({"_id": id}, {"$set": generate_apikey(str(id))})
    new_user = db.users.find_one({"_id": id})
    return new_user


def generate_apikey(id: str) -> dict:
    return {
        "api_key": hash(id)[-len(id):].upper(),
        "last_used_at": datetime.utcnow(),
        "usage_count": 0
    }


def read_user(item: dict, db: Database) -> dict:
    user = check_user_exists(item, db)
    return user


def delete_user(item: dict, db: Database) -> dict:
    user = check_user_exists(item, db)
    if not user:
        return user
    deleted_user = db.users.delete_one(user)
    return deleted_user


def update_usagecount(item: dict, db: Database) -> dict:
    user = db.users.find_one({"api_key": item["api_key"]})
    if not user:
        return user
    if user["usage_count"] > settings.QUERY_LIMIT:
        return "LIMIT"
    db.users.update_one({"api_key": item["api_key"]},
                        {"$inc": {"usage_count": 1},
                         "$set": {"last_used_at": datetime.utcnow()}})
    return db.users.find_one({"api_key": item["api_key"]})