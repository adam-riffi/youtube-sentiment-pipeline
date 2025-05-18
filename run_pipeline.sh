#!/bin/bash

echo "🛠️ Creating virtual environment..."
python -m venv .env

echo "🐍 Activating virtual environment..."
source .env/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📡 Running YouTube producer..."
python producers/youtube_producer.py

echo "🧠 Running comment sentiment processor..."
python processors/comment_sentiment_processor.py &

echo "📊 Launching Streamlit dashboard..."
streamlit run dashboard/app.py