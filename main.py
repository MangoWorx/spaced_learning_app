from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

app = FastAPI()

# Database simulation
database = {
    "users": {},
    "flashcards": {},
}

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
    if user.username in database["users"]:
        raise HTTPException(status_code=400, detail="User already exists")
    database["users"][user.username] = user
    return {"msg": "User created successfully"}

@app.post("/flashcards/create/")
async def create_flashcard(flashcard: Flashcard):
    if flashcard.user_id not in database["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    flashcard_id = len(database["flashcards"]) + 1
    flashcard.next_review = datetime.now() + timedelta(days=1)  # Simple spaced repetition implementation
    database["flashcards"][flashcard_id] = flashcard
    return {"msg": "Flashcard created successfully", "flashcard_id": flashcard_id}

@app.get("/flashcards/{user_id}/")
async def get_flashcards(user_id: str):
    if user_id not in database["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    user_flashcards = [fc for fc in database["flashcards"].values() if fc.user_id == user_id]
    return {"flashcards": user_flashcards}

@app.get("/flashcards/review/{user_id}/")
async def get_flashcards_for_review(user_id: str):
    if user_id not in database["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    due_flashcards = [fc for fc in database["flashcards"].values() if fc.user_id == user_id and fc.next_review <= datetime.now()]
    return {"flashcards": due_flashcards}