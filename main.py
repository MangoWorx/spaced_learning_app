from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.spaced_learning_app
users_collection = db.users
flashcards_collection = db.flashcards

# Models
class User(BaseModel):
    username: str
    email: str
    password: str
    created_at: datetime

class Flashcard(BaseModel):
    user_id: str
    question: str
    answer: str
    created_at: datetime
    next_review: datetime

# Routes
@app.post("/signup/")
async def signup(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="User already exists")
    users_collection.insert_one(user.dict())
    return {"msg": "User created successfully"}

@app.post("/flashcards/create/")
async def create_flashcard(flashcard: Flashcard):
    if not users_collection.find_one({"username": flashcard.user_id}):
        raise HTTPException(status_code=404, detail="User not found")
    flashcard_dict = flashcard.dict()
    flashcard_dict["next_review"] = datetime.now() + timedelta(days=1)  # Simple spaced repetition implementation
    flashcards_collection.insert_one(flashcard_dict)
    return {"msg": "Flashcard created successfully"}

@app.get("/flashcards/{user_id}/")
async def get_flashcards(user_id: str):
    if not users_collection.find_one({"username": user_id}):
        raise HTTPException(status_code=404, detail="User not found")
    user_flashcards = list(flashcards_collection.find({"user_id": user_id}))
    for flashcard in user_flashcards:
        flashcard["_id"] = str(flashcard["_id"])
    return {"flashcards": user_flashcards}

@app.get("/flashcards/review/{user_id}/")
async def get_flashcards_for_review(user_id: str):
    if not users_collection.find_one({"username": user_id}):
        raise HTTPException(status_code=404, detail="User not found")
    due_flashcards = list(flashcards_collection.find({"user_id": user_id, "next_review": {"$lte": datetime.now()}}))
    for flashcard in due_flashcards:
        flashcard["_id"] = str(flashcard["_id"])
    return {"flashcards": due_flashcards}