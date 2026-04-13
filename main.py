from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB


client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_prep"]
users_collection = db["users"]

# Model
class User(BaseModel):
    name: str
    email: str
    college: str
    year: str

# Signup API
@app.post("/signup")
def signup(user: User):
    users_collection.insert_one(user.dict())
    return {"message": "User saved"}

# Count API
@app.get("/count")
def get_count():
    count = users_collection.count_documents({})
    return {"count": count}