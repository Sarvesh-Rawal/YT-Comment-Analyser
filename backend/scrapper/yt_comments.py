from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import os
import re

# Load environment variables (API key)
load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL"""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1)

def fetch_youtube_comments(video_url: str) -> pd.DataFrame:

    # Extract video ID
    video_id = extract_video_id(video_url)

    # Initialize YouTube API client
    youtube = build("youtube", "v3", developerKey=api_key)

    comments = []
    next_page_token = None
    max_comments = 100

    video_response = youtube.videos().list(
    part="snippet",
    id=video_id
    ).execute()

    video_snippet = video_response["items"][0]["snippet"]
    upload_date = video_snippet["publishedAt"]
    video_title = video_snippet["title"]

    while True:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            published_at = snippet["publishedAt"]
            comment = snippet["textDisplay"]    

            comments.append({
                "post_ID": video_id,
                "time": published_at,
                "comment": comment
            })
            
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    # Convert to DataFrame
    df = pd.DataFrame(comments)
    return df, upload_date, video_title, video_id
