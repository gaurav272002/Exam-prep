import os
from googleapiclient.discovery import build

PREFERRED_CHANNELS = {
    "UCJjC1hn78yZqTf0vdTC6wAQ": "Gate Smashers",
    "UCul-fKVOFYTHdEag6bJrtFg": "Neso Academy",
}

_cache = {}


def search_videos_for_topic(topic, max_results=6):
    if topic in _cache:
        return _cache[topic]

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return []

    youtube = build("youtube", "v3", developerKey=api_key)

    response = youtube.search().list(
        part="snippet",
        q=topic,
        type="video",
        maxResults=max_results,
        relevanceLanguage="en"
    ).execute()

    videos = []
    for item in response.get("items", []):
        channel_id = item["snippet"]["channelId"]
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "channel_id": channel_id,
            "is_preferred": channel_id in PREFERRED_CHANNELS,
        })

    # preferred channels first, preserve relevance order within each group
    videos.sort(key=lambda v: 0 if v["is_preferred"] else 1)

    _cache[topic] = videos
    return videos
