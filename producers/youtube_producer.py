"""
youtube_producer.py

Fetches trending videos and comments from YouTube,
publishes them to Kafka topics, and writes metadata to disk for dashboard use.
"""

import os
import sys
import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from dotenv import load_dotenv
from pathlib import Path

# Add the scripts directory to Python path so we can import youtube_api
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.append(str(SCRIPT_DIR))
from youtube_api import fetch_multiple_regions, fetch_top_comments

# Load YOUTUBE_API_KEY from .env file
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY missing in .env")

# Kafka setup
BROKER = "localhost:9092"
VIDEO_TOPIC = "trending_videos"
COMMENT_TOPIC = "video_comments"

# Output path for dashboard to read video metadata
DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"
METADATA_FILE = DASHBOARD_DIR / "video_metadata.json"
os.makedirs(DASHBOARD_DIR, exist_ok=True)

# Start fresh with a new metadata file
if METADATA_FILE.exists():
    METADATA_FILE.unlink()

# Initialize Kafka producer
try:
    producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(2, 7, 0),
        retries=5,
        request_timeout_ms=20000
    )
except NoBrokersAvailable:
    print("❌ Kafka not reachable.")
    sys.exit(1)

def is_valid_video_id(video_id):
    """Returns True if the video_id is a valid YouTube video ID."""
    return isinstance(video_id, str) and len(video_id) == 11

def run_producer():
    # List of region codes to pull trending videos from
    regions = [
        "US", "IN", "BR", "RU", "JP", "MX", "DE", "FR", "GB", "KR",
        "ID", "TR", "VN", "TH", "EG", "NG", "PK", "IT", "ES", "CA"
    ]

    print("📡 Fetching trending videos...")
    videos = fetch_multiple_regions(regions)

    if not videos:
        print("⚠️ No videos returned from API.")
        return

    # Send metadata to Kafka and write to local file for Streamlit
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        for video in videos:
            video_id = video.get("video_id")

            if not is_valid_video_id(video_id):
                continue

            producer.send(VIDEO_TOPIC, video)

            # Prepare simplified metadata for dashboard use
            metadata = {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "title": video["title"],
                "region": video["region"]
            }
            f.write(json.dumps(metadata) + "\n")
            print(f"✅ Metadata: {metadata['title']} ({video_id})")

    print("💬 Fetching top comments...")
    for video in videos[:50]:  # Limit to avoid too many API calls
        video_id = video.get("video_id")
        region = video.get("region")

        if not is_valid_video_id(video_id):
            continue

        comments = fetch_top_comments(video_id, max_results=5)
        for comment in comments:
            comment["region"] = region  # Add region info to comment
            producer.send(COMMENT_TOPIC, comment)

    producer.flush()
    print("✅ All data sent.")

# Run when script is called directly
if __name__ == "__main__":
    run_producer()
