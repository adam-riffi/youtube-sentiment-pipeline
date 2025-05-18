# YouTube Real-Time Sentiment Pipeline

## 📦 Setup

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your YouTube API key:

```
YOUTUBE_API_KEY=your_api_key_here
```

## ▶️ Run

```bash
docker compose up -d        # Start Kafka
python producers/youtube_producer.py
python processors/comment_sentiment_processor.py
streamlit run dashboard/app.py
```

## 📁 Structure

- `producers/` → fetch trending videos + comments
- `processors/` → analyze sentiment
- `dashboard/` → Streamlit UI
- `scripts/` → YouTube API logic
- `.env.example` → template API config
- `requirements.txt` → dependencies

## ✅ Ready for GitHub or Docker.