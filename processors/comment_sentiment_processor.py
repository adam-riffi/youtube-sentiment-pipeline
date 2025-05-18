"""
comment_sentiment_processor.py

Consumes comments from the 'video_comments' Kafka topic,
performs sentiment analysis using HuggingFace transformers,
and publishes results to the 'comment_sentiment' Kafka topic.
"""

import os
import json
from kafka import KafkaConsumer, KafkaProducer
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables (if needed)
load_dotenv()

# Load a pretrained sentiment-analysis model from HuggingFace
# This will use the default 'distilbert-base-uncased-finetuned-sst-2-english'
sentiment_analyzer = pipeline("sentiment-analysis")

# Set up Kafka consumer to read incoming comments
consumer = KafkaConsumer(
    "video_comments",  # topic to read from
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="sentiment_processor"  # allow replay on new consumers
)

# Set up Kafka producer to send sentiment-labeled results
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Listen to incoming comments
for message in consumer:
    comment = message.value  # Deserialize Kafka message

    try:
        # Run HuggingFace model on the comment text
        result = sentiment_analyzer(comment["text"])[0]

        # Package the output with sentiment label + score
        output = {
            "video_id": comment["video_id"],
            "region": comment.get("region", ""),
            "text": comment["text"],
            "sentiment": result["label"].upper(),  # POSITIVE / NEGATIVE
            "score": round(result["score"], 4)
        }

        # Send processed message to next Kafka topic
        producer.send("comment_sentiment", output)

        # Log a short preview of what was sent
        print(f"✅ '{output['text'][:40]}...' → {output['sentiment']} ({output['score']})")

    except Exception as e:
        # Handle errors during sentiment processing
        print(f"⚠️ Error analyzing comment: {e}")
