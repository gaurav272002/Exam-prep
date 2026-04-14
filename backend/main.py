from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from openai import OpenAI
import PyPDF2
import io
import os
import json
import requests

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


# Upload syllabus
@app.post("/upload-syllabus")
async def upload_syllabus(file: UploadFile = File(...)):
    contents = await file.read()

    pdf = PyPDF2.PdfReader(io.BytesIO(contents))

    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"

    chunks = chunk_text(text)

    results = []
    for chunk in chunks:
        ai_output = extract_with_ai(chunk)
        results.append(ai_output)

    final_data = merge_results(results)

    return final_data

def chunk_text(text, chunk_size=2000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]






def extract_with_ai(chunk):
    prompt = f"""
You are an AI that extracts structured syllabus data.

From the given text, extract:

1. Semester (if present)
2. Subjects
3. Units inside each subject
4. Topics inside each unit

Return ONLY JSON in this format:

{{
  "Semester": {{
    "Subject Name": {{
      "Unit Name": ["topic1", "topic2"]
    }}
  }}
}}

Rules:
- Ignore extra text like guidelines, objectives, marks
- Only extract actual syllabus content
- Keep structure clean and consistent
- If semester not found, use "Unknown Semester"

Text:
{chunk}
"""
    print("In Ai ")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer ",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    result = response.json()
    print(result)
    return result["choices"][0]["message"]["content"]



def merge_results(results):
    final = {}

    for r in results:
        data = json.loads(r)

        for sem, subjects in data.items():
            if sem not in final:
                final[sem] = {}

            for subj, units in subjects.items():
                final[sem][subj] = units

    return final

