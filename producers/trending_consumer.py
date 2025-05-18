"""
trending_consumer.py

This is a utility script used for debugging or inspecting messages
on any Kafka topic in your pipeline. You can use it to view:
- raw video metadata
- incoming comments
- sentiment-processed messages
"""

from kafka import KafkaConsumer
import json

# Choose the topic you want to inspect:
# Options: "trending_videos", "video_comments", "comment_sentiment"
TOPIC = "comment_sentiment"

# Set up a Kafka consumer for the chosen topic
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",     # start from the beginning
    group_id="debug_consumer"         # separate group for debugging
)

print(f"🔎 Listening to topic '{TOPIC}'...")

# Print each message from Kafka as formatted JSON
for message in consumer:
    print(json.dumps(message.value, indent=2))
