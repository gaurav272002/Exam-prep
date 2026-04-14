# ExamPrep AI

Upload your college syllabus PDF and get a curated list of YouTube videos for every topic — no searching, no guessing.

## How It Works

1. Upload your syllabus PDF
2. AI extracts every topic from the syllabus structure (Semester > Subject > Unit > Topic)
3. YouTube is searched for each topic
4. Videos from Gate Smashers and Neso Academy are prioritized
5. Click any topic in the sidebar to watch videos directly on the page

## Stack

- **Backend:** FastAPI + Python
- **AI:** OpenRouter (GPT-4o-mini) for syllabus extraction
- **Videos:** YouTube Data API v3
- **Database:** MongoDB (user signups)
- **Frontend:** Plain HTML/CSS/JS

## Setup

### 1. Clone the repo

```
git clone https://github.com/gaurav272002/Exam-prep.git
cd Exam-prep
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Get API keys

**OpenRouter** (for AI syllabus extraction):
- Sign up at https://openrouter.ai
- Go to Keys and create a new key

**YouTube Data API v3** (for video search):
- Go to https://console.cloud.google.com
- Create a project
- Search for "YouTube Data API v3" and enable it
- Go to Credentials > Create Credentials > API Key

**MongoDB**:
- Use a free cluster at https://www.mongodb.com/atlas
- Copy the connection string

### 4. Configure .env

Fill in the values in the `.env` file at the project root:

```
OPENROUTER_API_KEY=your_openrouter_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
MONGO_URI=your_mongodb_connection_string_here
```

### 5. Run the backend

From the project root:

```
uvicorn backend.main:app --reload
```

### 6. Open the frontend

Open `frontend/index.html` in your browser. Make sure the API URL at the top of the script block is set to `http://127.0.0.1:8000` for local development.

## Project Structure

```
Exam-prep/
  backend/
    main.py        - FastAPI app (signup, syllabus upload, YouTube integration)
    youtube.py     - YouTube search with preferred channel ranking
  frontend/
    index.html     - Landing page + study UI
  requirements.txt
  .env             - API keys (not committed)
```

## Adding More Preferred Channels

Open `backend/youtube.py` and add entries to `PREFERRED_CHANNELS`:

```python
PREFERRED_CHANNELS = {
    "UCJjC1hn78yZqTf0vdTC6wAQ": "Gate Smashers",
    "UCul-fKVOFYTHdEag6bJrtFg": "Neso Academy",
    "YOUR_CHANNEL_ID_HERE": "Channel Name",
}
```

To find a channel's ID, go to the channel page on YouTube, click About, and look for the channel ID in the share options — or use a tool like https://commentpicker.com/youtube-channel-id.php.

## YouTube API Quota

The free YouTube Data API quota is 10,000 units/day. Each topic search costs 100 units, so you get roughly 100 topic searches per day. Repeated searches for the same topic are cached in memory and do not count against the quota.
