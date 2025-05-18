# 📊 YouTube Real-Time Sentiment Dashboard

This project builds a real-time pipeline that tracks trending YouTube videos, fetches comments, applies multilingual sentiment analysis using HuggingFace, and visualizes insights in a live dashboard built with Streamlit.

---

## 🚀 Features

- ⚡ Real-time ingestion of trending YouTube videos by region
- 💬 Top comment extraction and sentiment classification
- 🌍 Multilingual translation using Deep Translator
- 📈 Interactive dashboard with filters, word clouds, and CSV export
- 🐳 Fully Dockerized for portability

---

## 🛠️ Tech Stack

**Python · Kafka · HuggingFace · Streamlit · Docker**

---

## 📁 Project Structure

```
.
├── producers/                     # YouTube data ingestion
├── processors/                    # Sentiment analysis
├── dashboard/                     # Streamlit frontend
├── scripts/                       # YouTube API wrappers
├── docker/                        # Individual Dockerfiles
├── .env.example                   # Template for API key
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Kafka + Zookeeper
├── docker-compose.override.yml   # Pipeline services
├── run_pipeline.sh               # Optional local runner
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/your-username/youtube-sentiment-pipeline.git
cd youtube-sentiment-pipeline
```

### 2. Create your `.env` file
```env
YOUTUBE_API_KEY=your_actual_youtube_api_key
```

### 3. Start the full system with Docker
```bash
docker compose up --build
```

Then open the dashboard at:
```
http://localhost:8501
```

---

## 🧪 Local Manual Run (no Docker)
```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt

docker compose up -d   # Only for Kafka

python producers/youtube_producer.py
python processors/comment_sentiment_processor.py
streamlit run dashboard/app.py
```

---

## 📄 License

MIT – do anything you want, just credit the project.
