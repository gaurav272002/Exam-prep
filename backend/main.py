import io
import json
import os
import re

import PyPDF2
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

from backend.youtube import search_videos_for_topic

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_prep"]
users_collection = db["users"]


class User(BaseModel):
    name: str
    email: str
    college: str
    year: str


@app.post("/signup")
def signup(user: User):
    users_collection.insert_one(user.dict())
    return {"message": "User saved"}


@app.get("/count")
def get_count():
    count = users_collection.count_documents({})
    return {"count": count}


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

    syllabus = merge_results(results)

    # Attach YouTube videos for each topic
    for sem, subjects in syllabus.items():
        for subj, units in subjects.items():
            for unit, topics in units.items():
                topic_videos = {}
                for topic in topics:
                    topic_videos[topic] = search_videos_for_topic(topic)
                syllabus[sem][subj][unit] = topic_videos

    return syllabus


def chunk_text(text, chunk_size=2000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


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
    print("Calling AI...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
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
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?\s*", "", r).strip().rstrip("`").strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"Could not parse AI response: {cleaned[:200]}")
            continue

        for sem, subjects in data.items():
            if sem not in final:
                final[sem] = {}

            for subj, units in subjects.items():
                if subj not in final[sem]:
                    final[sem][subj] = {}
                for unit, topics in units.items():
                    if unit not in final[sem][subj]:
                        final[sem][subj][unit] = []
                    final[sem][subj][unit].extend(topics)

    return final
